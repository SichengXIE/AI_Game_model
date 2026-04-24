from __future__ import annotations

from typing import Any

from model_providers import load_provider_catalog


class ProviderCatalogService:
    def list(self) -> dict[str, Any]:
        catalog = load_provider_catalog()
        providers = [
            {
                "id": provider.id,
                "display_name": provider.display_name,
                "default_model": provider.default_model,
                "api_key_env": provider.api_key_env,
                "requires_api_key": provider.id != "local-demo",
                "supports_json_schema": provider.supports_json_schema,
                "supports_streaming": provider.supports_streaming,
                "notes": list(provider.notes),
            }
            for provider in catalog.list_enabled()
        ]
        return {
            "default_provider_id": catalog.default_provider_id,
            "providers": providers,
        }
