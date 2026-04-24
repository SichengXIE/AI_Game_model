import base64
import json
import sys
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from api.package_build import PackageBuildService
from api.spec_generation import SpecGenerationService


class LocalDemoProviderTests(unittest.TestCase):
    def test_demo_provider_generates_packageable_asset_spec_without_api_key(self):
        generation_service = SpecGenerationService(
            schema_path=ROOT / "schemas" / "asset-spec.schema.json"
        )

        spec_response = generation_service.generate(
            {
                "provider_id": "local-demo",
                "prompt": "生成一个现代风格的火车站，带玻璃大厅和清晰标识。",
            }
        )
        package_response = PackageBuildService().build(
            {"asset_spec": spec_response["asset_spec"]}
        )

        self.assertEqual(spec_response["status"], "ready")
        self.assertEqual(spec_response["provider_id"], "local-demo")
        self.assertEqual(spec_response["model"], "template-demo-v0.1")
        self.assertEqual(package_response["status"], "ready")

        decoded = base64.b64decode(package_response["zip_base64"])
        with zipfile.ZipFile(BytesIO(decoded), "r") as archive:
            active_asset = json.loads(archive.read("active-asset.json").decode("utf-8"))

        self.assertEqual(active_asset["metadata"]["asset_id"], "local-demo-template-station")
        self.assertIn("assembly", active_asset)

    def test_demo_provider_supports_compact_variant(self):
        service = SpecGenerationService(schema_path=ROOT / "schemas" / "asset-spec.schema.json")

        response = service.generate(
            {
                "provider_id": "local-demo",
                "prompt": "生成一个紧凑型郊区车站，占地小、入口少。",
            }
        )

        asset_spec = response["asset_spec"]
        self.assertEqual(response["status"], "ready")
        self.assertEqual(asset_spec["title"], "Compact Suburban Station Demo")
        self.assertEqual(asset_spec["connections"]["rail_tracks"], 2)


if __name__ == "__main__":
    unittest.main()
