"""Cooperative timeout/cancellation with owned tasks drained before returning."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable


class ExecutionCancelled(RuntimeError):
    pass


class ExecutionTimeout(TimeoutError):
    pass


async def run_cancellable[T](
    operation: Callable[[], Awaitable[T]],
    cancel: asyncio.Event,
    timeout: float | None,
) -> T:
    if cancel.is_set():
        raise ExecutionCancelled("cancelled before dispatch")
    if timeout is not None and timeout <= 0:
        raise ExecutionTimeout("deadline reached before dispatch")

    async def invoke() -> T:
        return await operation()

    work = asyncio.create_task(invoke())
    signal = asyncio.create_task(cancel.wait())
    try:
        done, _ = await asyncio.wait(
            {work, signal}, timeout=timeout, return_when=asyncio.FIRST_COMPLETED
        )
        if cancel.is_set():
            raise ExecutionCancelled("cancelled during execution")
        if work in done:
            return await work
        raise ExecutionTimeout("execution timeout")
    finally:
        work.cancel()
        signal.cancel()
        await asyncio.gather(work, signal, return_exceptions=True)
