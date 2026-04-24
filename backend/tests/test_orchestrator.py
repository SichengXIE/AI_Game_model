import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from model_providers.contracts import ChatResponse
from orchestrator import AssetSpecOrchestrator, OrchestrationRequest
from orchestrator.prompting import build_orchestrator_request


class FakeClient:
    def __init__(self, content):
        self.content = content
        self.last_request = None

    def complete(self, request):
        self.last_request = request
        return ChatResponse(
            provider_id="fake",
            model=request.model or "fake-model",
            content=self.content,
            raw={"choices": [{"message": {"content": self.content}}]},
        )


class AssetSpecOrchestratorTests(unittest.TestCase):
    def test_build_prompt_includes_schema_and_known_modules(self):
        request = build_orchestrator_request(
            user_prompt="港铁风格换乘站",
            schema_path=ROOT / "schemas" / "asset-spec.schema.json",
            model="test-model",
        )

        self.assertEqual(request.model, "test-model")
        self.assertEqual(request.response_format, {"type": "json_object"})
        prompt_context = json.loads(request.messages[1].content)
        self.assertIn("asset_spec_schema", prompt_context)
        self.assertIn("station.concourse.glass_hall", prompt_context["known_modules"])

    def test_ready_response_returns_valid_asset_spec(self):
        asset_spec = json.loads(
            (ROOT / "examples" / "asset-specs" / "hk-mtr-interchange-station.json").read_text(
                encoding="utf-8"
            )
        )
        content = json.dumps(
            {
                "status": "ready",
                "questions": [],
                "asset_spec": asset_spec,
                "design_explanation": "Uses a compact MTR-inspired station layout.",
                "template_rationale": ["Two island platforms provide four tracks."],
            },
            ensure_ascii=False,
        )
        orchestrator = AssetSpecOrchestrator(
            schema_path=ROOT / "schemas" / "asset-spec.schema.json",
            client=FakeClient(content),
        )

        result = orchestrator.run(
            OrchestrationRequest(user_prompt="我想做一个港铁风格的换乘站")
        )

        self.assertTrue(result.is_ready)
        self.assertEqual(result.asset_spec["subtype"], "interchange_station")
        self.assertEqual(result.validation_issues, ())

    def test_clarification_response_skips_asset_validation(self):
        content = json.dumps(
            {
                "status": "needs_clarification",
                "questions": [
                    {
                        "id": "station_size",
                        "question": "你希望车站是小型、中型还是大型？",
                        "reason": "规模会决定站台数和占地。",
                    }
                ],
                "asset_spec": None,
                "design_explanation": "Need station scale before choosing modules.",
                "template_rationale": [],
            },
            ensure_ascii=False,
        )
        orchestrator = AssetSpecOrchestrator(
            schema_path=ROOT / "schemas" / "asset-spec.schema.json",
            client=FakeClient(content),
        )

        result = orchestrator.run(OrchestrationRequest(user_prompt="做个车站"))

        self.assertEqual(result.status, "needs_clarification")
        self.assertEqual(len(result.questions), 1)
        self.assertEqual(result.validation_issues, ())

    def test_invalid_ready_spec_reports_validation_issues(self):
        content = json.dumps(
            {
                "status": "ready",
                "questions": [],
                "asset_spec": {
                    "spec_version": "0.1",
                    "game": "cities_skylines_2",
                    "asset_type": "train_station",
                    "title": "Broken Station",
                    "style": {
                        "theme": "modern_transit",
                        "regional_inspiration": "hong_kong",
                        "materials": ["glass"],
                    },
                    "footprint": {"width": 64, "length": 128, "height_class": "midrise"},
                    "modules": [{"module_id": "station.concourse.glass_hall", "count": 1}],
                    "connections": {"rail_tracks": 4, "road_access": 1, "pedestrian_entries": 2},
                    "decor": {"sign_language": ["zh-HK", "en"], "color_palette": ["#C8102E"]},
                    "runtime_constraints": {
                        "template_only": True,
                        "requires_base_mod": True,
                        "base_mod_min_version": "0.1.0",
                    },
                },
                "design_explanation": "",
                "template_rationale": [],
            },
            ensure_ascii=False,
        )
        orchestrator = AssetSpecOrchestrator(
            schema_path=ROOT / "schemas" / "asset-spec.schema.json",
            client=FakeClient(content),
        )

        result = orchestrator.run(OrchestrationRequest(user_prompt="broken"))

        self.assertEqual(result.status, "invalid")
        codes = {issue.code for issue in result.validation_issues}
        self.assertIn("missing_platform", codes)
        self.assertIn("missing_entrance", codes)


if __name__ == "__main__":
    unittest.main()
