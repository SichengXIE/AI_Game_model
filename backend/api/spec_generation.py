from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Optional

from orchestrator import AssetSpecOrchestrator, OrchestrationRequest, OrchestrationResult


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class SpecGenerationService:
    def __init__(
        self,
        schema_path: Path,
        orchestrator: Optional[AssetSpecOrchestrator] = None,
    ):
        self.schema_path = schema_path
        self.orchestrator = orchestrator or AssetSpecOrchestrator(schema_path=schema_path)

    def generate(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        prompt = payload.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ApiError(400, "missing_prompt", "Request body must include a non-empty prompt.")

        provider_id = payload.get("provider_id")
        model = payload.get("model")
        user_constraints = payload.get("user_constraints", {})
        existing_answers = payload.get("existing_answers", {})

        if provider_id is not None and not isinstance(provider_id, str):
            raise ApiError(400, "invalid_provider_id", "provider_id must be a string.")
        if model is not None and not isinstance(model, str):
            raise ApiError(400, "invalid_model", "model must be a string.")
        if not isinstance(user_constraints, Mapping):
            raise ApiError(400, "invalid_user_constraints", "user_constraints must be an object.")
        if not isinstance(existing_answers, Mapping):
            raise ApiError(400, "invalid_existing_answers", "existing_answers must be an object.")

        result = self.orchestrator.run(
            OrchestrationRequest(
                user_prompt=prompt.strip(),
                provider_id=provider_id,
                model=model,
                user_constraints=user_constraints,
                existing_answers=existing_answers,
            )
        )
        return result_to_payload(result)


def result_to_payload(result: OrchestrationResult) -> dict[str, Any]:
    return {
        "status": result.status,
        "asset_spec": result.asset_spec,
        "design_explanation": result.design_explanation,
        "template_rationale": list(result.template_rationale),
        "questions": [asdict(question) for question in result.questions],
        "validation_issues": [asdict(issue) for issue in result.validation_issues],
        "provider_id": result.provider_id,
        "model": result.model,
    }
