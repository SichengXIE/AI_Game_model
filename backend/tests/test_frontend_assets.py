import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FrontendAssetTests(unittest.TestCase):
    def test_web_mvp_calls_generation_and_package_endpoints(self):
        app_js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

        self.assertIn("/api/specs/generate", app_js)
        self.assertIn("/api/packages/build", app_js)
        self.assertIn("zip_base64", app_js)

    def test_index_loads_frontend_assets(self):
        index_html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")

        self.assertIn("/styles.css", index_html)
        self.assertIn("/app.js", index_html)
        self.assertIn("生成 Asset Spec 并打包", index_html)


if __name__ == "__main__":
    unittest.main()
