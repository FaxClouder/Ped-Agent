from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

from ped_agent.agent.contracts import AnswerDocument, EvidenceItem, RunStatus
from ped_agent.agent.evidence_graph import RunCancelled

from ped_agent_server.agent_repository import AgentRepository

EventEmitter = Callable[[str, dict[str, object]], Awaitable[None]]
CancellationCheck = Callable[[], bool]


@dataclass(frozen=True)
class RunExecutionContext:
    run_id: str
    conversation_id: str
    query: str
    recent_messages: list[dict[str, object]]
    previous_evidence_ids: list[str]


@dataclass(frozen=True)
class RunExecutionResult:
    answer: AnswerDocument
    evidence: list[EvidenceItem]


class RunExecutor(Protocol):
    async def execute(
        self,
        context: RunExecutionContext,
        emit: EventEmitter,
        is_cancelled: CancellationCheck,
    ) -> RunExecutionResult: ...


class RunService:
    def __init__(
        self,
        repository: AgentRepository,
        executor: RunExecutor,
        *,
        max_concurrent_runs: int = 2,
        recent_message_limit: int = 6,
    ) -> None:
        self.repository = repository
        self.executor = executor
        self._semaphore = asyncio.Semaphore(max_concurrent_runs)
        self._recent_message_limit = recent_message_limit
        self._tasks: dict[str, asyncio.Task[None]] = {}

    async def submit(self, conversation_id: str, query: str) -> dict[str, object]:
        run = self.repository.create_run(conversation_id, query=query)
        self.repository.add_message(conversation_id, role="user", content=query)
        task = asyncio.create_task(self._execute(run), name=f"ped-agent-run-{run['id']}")
        self._tasks[str(run["id"])] = task
        task.add_done_callback(lambda _: self._tasks.pop(str(run["id"]), None))
        return run

    async def wait(self, run_id: str) -> None:
        task = self._tasks.get(run_id)
        if task is not None:
            await asyncio.shield(task)

    async def shutdown(self) -> None:
        tasks = list(self._tasks.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute(self, run: dict[str, object]) -> None:
        run_id = str(run["id"])
        async with self._semaphore:
            if self.repository.is_cancel_requested(run_id):
                return
            self.repository.set_run_status(run_id, RunStatus.RUNNING)
            self.repository.append_event(
                run_id,
                "run.started",
                {"run_id": run_id, "status": RunStatus.RUNNING.value},
            )
            try:
                context = self._build_context(run)
                result = await self.executor.execute(
                    context,
                    lambda event, payload: self._emit(run_id, event, payload),
                    lambda: self.repository.is_cancel_requested(run_id),
                )
                if self.repository.is_cancel_requested(run_id):
                    return
                self._ensure_displayable(result.answer)
                message_id = self._persist_result(run, result)
                self.repository.append_event(
                    run_id,
                    "answer.delta",
                    {"delta": result.answer.answer_markdown, "verified": True},
                )
                self.repository.set_run_status(run_id, RunStatus.COMPLETED)
                self.repository.append_event(
                    run_id,
                    "run.completed",
                    {"run_id": run_id, "message_id": message_id},
                )
            except asyncio.CancelledError:
                if not self.repository.is_cancel_requested(run_id):
                    self.repository.set_run_status(
                        run_id,
                        RunStatus.INTERRUPTED,
                        error="service shutdown",
                    )
                raise
            except RunCancelled:
                if not self.repository.is_cancel_requested(run_id):
                    self.repository.request_cancel(run_id)
            # The run boundary must translate every provider/graph failure into a
            # terminal, redacted event so background task exceptions never leak.
            except Exception as exc:  # noqa: BLE001
                self.repository.set_run_status(
                    run_id,
                    RunStatus.FAILED,
                    error=type(exc).__name__,
                )
                self.repository.append_event(
                    run_id,
                    "run.failed",
                    {"run_id": run_id, "error": "run execution failed"},
                )

    def _build_context(self, run: dict[str, object]) -> RunExecutionContext:
        conversation_id = str(run["conversation_id"])
        detail = self.repository.get_conversation(conversation_id) or {"messages": []}
        messages = list(detail["messages"])[-self._recent_message_limit :]
        previous_ids: list[str] = []
        for message in reversed(messages[:-1]):
            citations = message.get("citations", [])
            if citations:
                previous_ids = [str(item["evidence"]["evidence_id"]) for item in citations]
                break
        return RunExecutionContext(
            run_id=str(run["id"]),
            conversation_id=conversation_id,
            query=str(run["query"]),
            recent_messages=messages,
            previous_evidence_ids=previous_ids,
        )

    async def _emit(self, run_id: str, event: str, payload: dict[str, object]) -> None:
        self.repository.append_event(run_id, event, payload)

    def _persist_result(self, run: dict[str, object], result: RunExecutionResult) -> str:
        run_id = str(run["id"])
        self.repository.save_evidence(
            run_id,
            [item.model_dump(mode="json") for item in result.evidence],
        )
        message = self.repository.add_message(
            str(run["conversation_id"]),
            role="assistant",
            content=result.answer.answer_markdown,
            answer_document=result.answer.model_dump(mode="json"),
        )
        for citation in result.answer.citations:
            self.repository.link_citation(
                str(message["id"]),
                citation.label,
                citation.evidence_id,
                citation.claim_ids,
            )
        return str(message["id"])

    @staticmethod
    def _ensure_displayable(answer: AnswerDocument) -> None:
        if not answer.verification.rules_passed:
            raise ValueError("answer failed citation rules")
        if answer.verification.status == "verified" and not answer.verification.semantic_passed:
            raise ValueError("answer failed semantic verification")
