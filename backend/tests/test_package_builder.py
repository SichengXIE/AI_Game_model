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
from api.spec_generation import ApiError
from package_builder import PackageBuilder, PackageBuildError


def load_example_spec():
    return json.loads(
        (ROOT / "examples" / "asset-specs" / "hk-mtr-interchange-station.json").read_text(
            encoding="utf-8"
        )
    )


class PackageBuilderTests(unittest.TestCase):
    def test_builds_expected_zip_files(self):
        package = PackageBuilder().build(load_example_spec())

        with zipfile.ZipFile(BytesIO(package.zip_bytes), "r") as archive:
            names = set(archive.namelist())
            active_asset = json.loads(archive.read("active-asset.json").decode("utf-8"))
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            preview = json.loads(archive.read("preview.json").decode("utf-8"))
            readme = archive.read("README.md").decode("utf-8")

        self.assertEqual(
            names,
            {"active-asset.json", "manifest.json", "preview.json", "README.md"},
        )
        self.assertEqual(active_asset["title"], "Harbor MTR-Style Interchange")
        self.assertEqual(manifest["assembly"]["component_count"], 6)
        self.assertEqual(preview["assembly_summary"]["anchors"][0]["type"], "rail_track")
        self.assertIn("Base Mod minimum version", readme)

    def test_invalid_spec_raises_package_error(self):
        asset_spec = load_example_spec()
        asset_spec["modules"] = []

        with self.assertRaises(PackageBuildError) as raised:
            PackageBuilder().build(asset_spec)

        self.assertEqual(raised.exception.code, "invalid_asset_spec")

    def test_api_service_returns_base64_zip(self):
        response = PackageBuildService().build({"asset_spec": load_example_spec()})

        self.assertEqual(response["status"], "ready")
        decoded = base64.b64decode(response["zip_base64"])
        with zipfile.ZipFile(BytesIO(decoded), "r") as archive:
            self.assertIn("active-asset.json", archive.namelist())

    def test_package_id_falls_back_to_safe_ascii_slug(self):
        asset_spec = load_example_spec()
        asset_spec.pop("metadata")
        asset_spec["title"] = "港铁风格换乘站"

        package = PackageBuilder().build(asset_spec)

        self.assertTrue(package.package_id.startswith("untitled-station-"))
        self.assertTrue(package.filename.endswith(".zip"))

    def test_api_service_requires_asset_spec_object(self):
        with self.assertRaises(ApiError) as raised:
            PackageBuildService().build({})

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(raised.exception.code, "missing_asset_spec")

    def test_api_service_returns_invalid_payload_for_bad_spec(self):
        asset_spec = load_example_spec()
        asset_spec["decor"]["color_palette"] = ["red"]

        response = PackageBuildService().build({"asset_spec": asset_spec})

        self.assertEqual(response["status"], "invalid")
        self.assertEqual(response["error"]["code"], "invalid_asset_spec")


if __name__ == "__main__":
    unittest.main()
