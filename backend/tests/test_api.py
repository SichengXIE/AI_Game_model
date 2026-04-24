import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from api.spec_generation import ApiError, SpecGenerationService
from orchestrator.contracts import OrchestrationResult


class FakeOrchestrator:
    def __init__(self):
        self.last_request = None

    def run(self, request):
        self.last_request = request
        return OrchestrationResult(
            status="ready",
            asset_spec={
                "spec_version": "0.1",
                "game": "cities_skylines_2",
                "asset_type": "train_station",
                "title": "Test Station",
            },
            design_explanation="A compact station assembled from template components.",
            template_rationale=("Selected station shell and entrance modules.",),
            provider_id=request.provider_id,
            model=request.model,
        )


class SpecGenerationServiceTests(unittest.TestCase):
    def test_generate_passes_provider_model_and_prompt_to_orchestrator(self):
        orchestrator = FakeOrchestrator()
        service = SpecGenerationService(
            schema_path=ROOT / "schemas" / "asset-spec.schema.json",
            orchestrator=orchestrator,
        )

        response = service.generate(
            {
                "provider_id": "qwen-hk",
                "model": "qwen-plus-latest",
                "prompt": "我想做一个港铁风格的换乘站",
                "user_constraints": {"include_assembly": True},
            }
        )

        self.assertEqual(response["status"], "ready")
        self.assertEqual(response["provider_id"], "qwen-hk")
        self.assertEqual(response["model"], "qwen-plus-latest")
        self.assertEqual(orchestrator.last_request.provider_id, "qwen-hk")
        self.assertEqual(orchestrator.last_request.model, "qwen-plus-latest")
        self.assertEqual(orchestrator.last_request.user_constraints["include_assembly"], True)

    def test_missing_prompt_returns_api_error(self):
        service = SpecGenerationService(
            schema_path=ROOT / "schemas" / "asset-spec.schema.json",
            orchestrator=FakeOrchestrator(),
        )

        with self.assertRaises(ApiError) as raised:
            service.generate({"provider_id": "qwen-hk"})

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(raised.exception.code, "missing_prompt")

    def test_result_payload_is_json_serializable(self):
        service = SpecGenerationService(
            schema_path=ROOT / "schemas" / "asset-spec.schema.json",
            orchestrator=FakeOrchestrator(),
        )

        response = service.generate({"prompt": "station"})

        json.dumps(response, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
