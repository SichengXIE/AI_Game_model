import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from api.providers import ProviderCatalogService


class ProviderCatalogServiceTests(unittest.TestCase):
    def test_lists_enabled_providers_without_transport_details(self):
        response = ProviderCatalogService().list()

        provider_ids = {provider["id"] for provider in response["providers"]}
        self.assertEqual(response["default_provider_id"], "qwen-hk")
        self.assertIn("qwen-hk", provider_ids)
        self.assertIn("openai", provider_ids)

        for provider in response["providers"]:
            self.assertIn("default_model", provider)
            self.assertIn("api_key_env", provider)
            self.assertNotIn("base_url", provider)


if __name__ == "__main__":
    unittest.main()
