from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Union

from .catalog import ProviderCatalog, load_provider_catalog
from .contracts import ChatMessage, ChatRequest, ChatResponse
from .openai_compatible import OpenAICompatibleClient


def build_asset_spec_request(user_prompt: str, schema_path: Union[str, Path]) -> ChatRequest:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    return ChatRequest(
        messages=[
            ChatMessage(
                role="system",
                content=(
                    "You generate only valid JSON Asset Spec v0.1 for Cities: "
                    "Skylines II train station assets. Do not return Markdown."
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    "Create an Asset Spec for this request:\n"
                    f"{user_prompt}\n\n"
                    "The output must satisfy this JSON Schema:\n"
                    f"{json.dumps(schema, ensure_ascii=False)}"
                ),
            ),
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )


def generate_asset_spec_json(
    user_prompt: str,
    schema_path: Union[str, Path],
    provider_id: Optional[str] = None,
    catalog: Optional[ProviderCatalog] = None,
) -> ChatResponse:
    provider_catalog = catalog or load_provider_catalog()
    provider = provider_catalog.get(provider_id)
    client = OpenAICompatibleClient(provider)
    request = build_asset_spec_request(user_prompt=user_prompt, schema_path=schema_path)
    return client.complete(request)
