import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from model_providers import ChatMessage, ChatRequest, OpenAICompatibleClient, load_provider_catalog
from model_providers.contracts import ProviderConfig


class ModelProviderTests(unittest.TestCase):
    def test_default_catalog_exposes_expected_providers(self):
        catalog = load_provider_catalog()
        providers = {provider.id for provider in catalog.list_enabled()}

        self.assertIn("gemini", providers)
        self.assertIn("qwen-hk", providers)
        self.assertIn("doubao-ark", providers)

    def test_openai_compatible_payload_uses_default_model(self):
        provider = ProviderConfig(
            id="test",
            display_name="Test",
            api_style="openai_chat_completions",
            base_url="https://example.com/v1/",
            api_key_env="TEST_API_KEY",
            default_model="test-model",
        )
        client = OpenAICompatibleClient(provider)
        payload = client.build_payload(
            ChatRequest(
                messages=[ChatMessage(role="user", content="hello")],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
        )

        self.assertEqual(payload["model"], "test-model")
        self.assertEqual(payload["messages"], [{"role": "user", "content": "hello"}])
        self.assertEqual(payload["temperature"], 0.1)
        self.assertEqual(payload["response_format"], {"type": "json_object"})

    def test_chat_completions_url_normalizes_base_url(self):
        provider = ProviderConfig(
            id="test",
            display_name="Test",
            api_style="openai_chat_completions",
            base_url="https://example.com/v1/",
            api_key_env="TEST_API_KEY",
            default_model="test-model",
        )
        client = OpenAICompatibleClient(provider)

        self.assertEqual(
            client._chat_completions_url(),
            "https://example.com/v1/chat/completions",
        )

    def test_example_provider_config_is_valid_json(self):
        config_path = ROOT / "examples" / "model-providers.example.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))

        self.assertEqual(config["schema_version"], "0.1")
        self.assertGreaterEqual(len(config["providers"]), 4)

    def test_missing_api_key_fails_before_network_call(self):
        provider = ProviderConfig(
            id="test",
            display_name="Test",
            api_style="openai_chat_completions",
            base_url="https://example.com/v1",
            api_key_env="TEST_API_KEY_DOES_NOT_EXIST",
            default_model="test-model",
        )
        client = OpenAICompatibleClient(provider)

        os.environ.pop("TEST_API_KEY_DOES_NOT_EXIST", None)
        with self.assertRaisesRegex(RuntimeError, "Missing API key"):
            client.complete(ChatRequest(messages=[ChatMessage(role="user", content="hello")]))


if __name__ == "__main__":
    unittest.main()
