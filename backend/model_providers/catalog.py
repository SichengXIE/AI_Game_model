from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional, Union

from .contracts import ProviderConfig


DEFAULT_PROVIDER_CONFIG: dict[str, Any] = {
    "schema_version": "0.1",
    "default_provider_id": "qwen-hk",
    "providers": [
        {
            "id": "openai",
            "display_name": "OpenAI",
            "api_style": "openai_chat_completions",
            "base_url": "https://api.openai.com/v1",
            "api_key_env": "OPENAI_API_KEY",
            "default_model": "gpt-5.4",
            "enabled": True,
            "supports_json_schema": True,
            "supports_streaming": True,
            "timeout_seconds": 60,
        },
        {
            "id": "gemini",
            "display_name": "Google Gemini",
            "api_style": "openai_chat_completions",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "api_key_env": "GEMINI_API_KEY",
            "default_model": "gemini-3-flash-preview",
            "enabled": True,
            "supports_json_schema": True,
            "supports_streaming": True,
            "timeout_seconds": 60,
        },
        {
            "id": "qwen-hk",
            "display_name": "Qwen DashScope Hong Kong",
            "api_style": "openai_chat_completions",
            "base_url": "https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key_env": "DASHSCOPE_API_KEY",
            "default_model": "qwen-plus-latest",
            "enabled": True,
            "supports_json_schema": True,
            "supports_streaming": True,
            "timeout_seconds": 60,
        },
        {
            "id": "doubao-ark",
            "display_name": "Doubao Volcengine Ark",
            "api_style": "openai_chat_completions",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "api_key_env": "ARK_API_KEY",
            "default_model": "doubao-seed-1-6-251015",
            "enabled": True,
            "supports_json_schema": False,
            "supports_streaming": True,
            "timeout_seconds": 60,
            "notes": [
                "For Ark custom endpoints, users may replace default_model with their endpoint ID.",
                "Coding Plan users may prefer https://ark.cn-beijing.volces.com/api/coding/v3.",
            ],
        },
    ],
}


class ProviderCatalog:
    def __init__(self, config: Mapping[str, Any]):
        self.default_provider_id = str(config["default_provider_id"])
        self._providers = {
            provider.id: provider
            for provider in (
                ProviderConfig.from_dict(provider_data)
                for provider_data in config.get("providers", [])
            )
        }

    def get(self, provider_id: Optional[str] = None) -> ProviderConfig:
        resolved_id = provider_id or self.default_provider_id
        try:
            provider = self._providers[resolved_id]
        except KeyError as error:
            raise KeyError(f"Unknown model provider: {resolved_id}") from error

        if not provider.enabled:
            raise ValueError(f"Model provider is disabled: {resolved_id}")

        return provider

    def list_enabled(self) -> list[ProviderConfig]:
        return [provider for provider in self._providers.values() if provider.enabled]


def load_provider_catalog(path: Optional[Union[str, Path]] = None) -> ProviderCatalog:
    if path is None:
        return ProviderCatalog(DEFAULT_PROVIDER_CONFIG)

    with Path(path).open("r", encoding="utf-8") as config_file:
        return ProviderCatalog(json.load(config_file))
