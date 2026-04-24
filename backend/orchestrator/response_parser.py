from __future__ import annotations

import json
from typing import Any, Mapping

from .contracts import ClarifyingQuestion, OrchestrationResult, ValidationIssue


def parse_orchestrator_response(
    content: str,
    provider_id: str,
    model: str,
) -> OrchestrationResult:
    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        return OrchestrationResult(
            status="invalid",
            validation_issues=(
                ValidationIssue(
                    code="invalid_json",
                    message=f"Model response was not valid JSON: {error.msg}",
                    path="$",
                ),
            ),
            provider_id=provider_id,
            model=model,
            raw_model_content=content,
        )

    if not isinstance(data, Mapping):
        return OrchestrationResult(
            status="invalid",
            validation_issues=(
                ValidationIssue(
                    code="invalid_response_shape",
                    message="Model response root must be an object.",
                    path="$",
                ),
            ),
            provider_id=provider_id,
            model=model,
            raw_model_content=content,
        )

    status = str(data.get("status", "invalid"))
    questions = tuple(
        ClarifyingQuestion.from_dict(question)
        for question in data.get("questions", [])
        if isinstance(question, Mapping)
    )

    if status == "needs_clarification":
        return OrchestrationResult(
            status="needs_clarification",
            questions=questions,
            design_explanation=str(data.get("design_explanation", "")),
            template_rationale=tuple(_as_string_list(data.get("template_rationale", []))),
            provider_id=provider_id,
            model=model,
            raw_model_content=content,
        )

    if status != "ready":
        return OrchestrationResult(
            status="invalid",
            validation_issues=(
                ValidationIssue(
                    code="unsupported_status",
                    message=f"Unsupported orchestrator status: {status}",
                    path="$.status",
                ),
            ),
            provider_id=provider_id,
            model=model,
            raw_model_content=content,
        )

    asset_spec = data.get("asset_spec")
    if not isinstance(asset_spec, Mapping):
        return OrchestrationResult(
            status="invalid",
            validation_issues=(
                ValidationIssue(
                    code="missing_asset_spec",
                    message="Ready responses must include asset_spec object.",
                    path="$.asset_spec",
                ),
            ),
            provider_id=provider_id,
            model=model,
            raw_model_content=content,
        )

    return OrchestrationResult(
        status="ready",
        asset_spec=asset_spec,
        design_explanation=str(data.get("design_explanation", "")),
        template_rationale=tuple(_as_string_list(data.get("template_rationale", []))),
        questions=questions,
        provider_id=provider_id,
        model=model,
        raw_model_content=content,
    )


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
