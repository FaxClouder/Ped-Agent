from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from ped_contracts.evidence import ModelOutput
from ped_research_agent.ports import ModelGateway, StructuredOutputUnsupported

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)
NativeStructuredCall = Callable[
    [str, type[BaseModel]], Awaitable[tuple[BaseModel | None, ModelOutput]]
]
TextCall = Callable[[str], Awaitable[ModelOutput]]


async def structured_generate(  # noqa: UP047 - shared TypeVar also binds the helpers below.
    gateway: ModelGateway,
    prompt: str,
    model: type[StructuredModel],
) -> tuple[StructuredModel, str]:
    """Answer-model structured output; returns the parsed value and the model name."""
    return await _structured(
        getattr(gateway, "generate_structured", None), gateway.generate, prompt, model
    )


async def structured_verify(  # noqa: UP047 - shared TypeVar also binds the helpers below.
    gateway: ModelGateway,
    prompt: str,
    model: type[StructuredModel],
) -> tuple[StructuredModel, str]:
    """Verifier-model structured output; repairs stay on the verifier model."""
    return await _structured(
        getattr(gateway, "verify_structured", None), gateway.verify, prompt, model
    )


async def _structured(  # noqa: UP047 - shared TypeVar also binds the helpers below.
    native: NativeStructuredCall | None,
    invoke: TextCall,
    prompt: str,
    model: type[StructuredModel],
) -> tuple[StructuredModel, str]:
    if callable(native):
        try:
            value, raw = await native(prompt, model)
        except (StructuredOutputUnsupported, NotImplementedError):
            pass
        else:
            if value is not None:
                try:
                    return model.model_validate(value), raw.model
                except (TypeError, ValueError):
                    pass
            return await repair_structured(prompt, raw, model, invoke)

    output = await invoke(prompt)
    try:
        return parse_structured(output.content, model), output.model
    except (ValidationError, ValueError, json.JSONDecodeError):
        return await repair_structured(prompt, output, model, invoke)


async def repair_structured(  # noqa: UP047 - shared TypeVar also binds the helpers above.
    prompt: str,
    raw: ModelOutput,
    model: type[StructuredModel],
    invoke: TextCall,
) -> tuple[StructuredModel, str]:
    repaired = await invoke(
        "Repair the response into valid JSON matching the requested schema. "
        "Return JSON only.\n"
        f"Original task:\n{prompt}\n"
        f"Invalid response:\n{raw.content or '[empty response]'}"
    )
    return parse_structured(repaired.content, model), repaired.model


def parse_structured(  # noqa: UP047 - shared TypeVar also binds the helpers above.
    content: str,
    model: type[StructuredModel],
) -> StructuredModel:
    normalized = content.strip()
    if normalized.startswith("```"):
        normalized = normalized.split("\n", 1)[-1].rsplit("```", 1)[0]
    return model.model_validate_json(normalized)
