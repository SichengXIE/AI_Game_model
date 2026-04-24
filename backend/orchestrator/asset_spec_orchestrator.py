from __future__ import annotations

from pathlib import Path
from typing import Optional, Protocol, Union

from model_providers import OpenAICompatibleClient, load_provider_catalog
from model_providers.contracts import ChatRequest, ChatResponse

from .contracts import OrchestrationRequest, OrchestrationResult
from .prompting import build_orchestrator_request
from .response_parser import parse_orchestrator_response
from .spec_validator import validate_asset_spec_contract


class ChatClient(Protocol):
    def complete(self, request: ChatRequest) -> ChatResponse:
        ...


class AssetSpecOrchestrator:
    def __init__(
        self,
        schema_path: Union[str, Path],
        client: Optional[ChatClient] = None,
    ):
        self.schema_path = Path(schema_path)
        self.client = client

    def run(self, request: OrchestrationRequest) -> OrchestrationResult:
        chat_request = build_orchestrator_request(
            user_prompt=request.user_prompt,
            schema_path=self.schema_path,
            model=request.model,
            user_constraints=request.user_constraints,
            existing_answers=request.existing_answers,
        )

        client = self.client or self._build_client(request.provider_id)
        response = client.complete(chat_request)
        result = parse_orchestrator_response(
            content=response.content,
            provider_id=response.provider_id,
            model=response.model,
        )

        if result.status != "ready" or result.asset_spec is None:
            return result

        issues = validate_asset_spec_contract(result.asset_spec)
        if issues:
            return OrchestrationResult(
                status="invalid",
                asset_spec=result.asset_spec,
                design_explanation=result.design_explanation,
                template_rationale=result.template_rationale,
                questions=result.questions,
                validation_issues=issues,
                provider_id=result.provider_id,
                model=result.model,
                raw_model_content=result.raw_model_content,
            )

        return result

    @staticmethod
    def _build_client(provider_id: Optional[str]) -> OpenAICompatibleClient:
        provider = load_provider_catalog().get(provider_id)
        return OpenAICompatibleClient(provider)
