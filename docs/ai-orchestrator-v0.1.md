# AI Orchestrator v0.1

The AI Orchestrator turns user intent into a validated `Asset Spec v0.1`.

It does not call game APIs, compile DLLs, or trust raw model output. Its job is to ask for missing information when needed, choose template modules from the allowed module list, generate a spec candidate, explain the design, and hand validated output to the next backend stage.

## 1. Responsibilities

1. Understand natural-language requests
2. Extract style, footprint, modules, connections, colors, and constraints
3. Select only known template modules
4. Generate a user-facing design explanation
5. Ask clarifying questions when the request is too underspecified
6. Validate `Asset Spec` before returning a ready result

## 2. Response Envelope

The model must return a JSON envelope:

```json
{
  "status": "ready",
  "questions": [],
  "asset_spec": {},
  "design_explanation": "Short explanation for the user.",
  "template_rationale": ["Why selected modules fit the request."]
}
```

When the request is underspecified:

```json
{
  "status": "needs_clarification",
  "questions": [
    {
      "id": "station_size",
      "question": "你希望车站是小型、中型还是大型？",
      "reason": "规模会决定占地、站台数和入口数量。"
    }
  ],
  "asset_spec": null,
  "design_explanation": "Need more information before selecting modules.",
  "template_rationale": []
}
```

## 3. Validation

The orchestrator validates the model output in two layers:

1. JSON envelope validation
2. `Asset Spec` contract validation

The current Python validator checks the executable contract used by the Base Mod proof of concept:

1. `spec_version`, `game`, and `asset_type`
2. required style fields
3. footprint size and height class
4. known module IDs
5. at least one platform module
6. at least one entrance module
7. rail, road, and pedestrian connection counts
8. sign languages and color palette
9. Base Mod runtime constraints

## 4. Backend Entry Points

Code lives in:

```text
backend/orchestrator/
```

Use:

```python
from orchestrator import AssetSpecOrchestrator, OrchestrationRequest

orchestrator = AssetSpecOrchestrator(schema_path="schemas/asset-spec.schema.json")
result = orchestrator.run(
    OrchestrationRequest(
        user_prompt="我想做一个港铁风格的换乘站",
        provider_id="qwen-hk",
    )
)
```

If `result.status == "ready"`, pass `result.asset_spec` to the package builder.

If `result.status == "needs_clarification"`, show `result.questions` to the user.

If `result.status == "invalid"`, show or log `result.validation_issues` and request one model repair attempt later.

## 5. Current Limits

1. v0.1 validates the executable core contract, not every optional JSON Schema field.
2. Repair attempts are not implemented yet.
3. Provider calls use the existing OpenAI-compatible client.
4. This layer returns JSON-ready Python objects; no FastAPI endpoint is wired yet.

The next implementation step is `POST /api/specs/generate`, which should call this orchestrator and return the envelope to the frontend.
