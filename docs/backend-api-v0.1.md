# Backend API v0.1

The first backend API exposes AI Orchestrator through a JSON endpoint.

## Run Locally

```bash
python backend/api/server.py
```

The server listens on:

```text
http://127.0.0.1:8000
```

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Generate Asset Spec

```http
POST /api/specs/generate
Content-Type: application/json
```

Request:

```json
{
  "provider_id": "qwen-hk",
  "model": "qwen-plus-latest",
  "prompt": "我想做一个港铁风格的换乘站",
  "user_constraints": {
    "include_assembly": true
  }
}
```

Response when ready:

```json
{
  "status": "ready",
  "asset_spec": {},
  "design_explanation": "...",
  "template_rationale": [],
  "questions": [],
  "validation_issues": [],
  "provider_id": "qwen-hk",
  "model": "qwen-plus-latest"
}
```

Response when more information is needed:

```json
{
  "status": "needs_clarification",
  "asset_spec": null,
  "questions": [
    {
      "id": "station_size",
      "question": "你希望车站是小型、中型还是大型？",
      "reason": "规模会影响站台数、入口和占地。"
    }
  ]
}
```

## 3D Assembly Requirement

For user requests that imply a visible station shell, facade, or game-ready placement, the model should include `asset_spec.assembly`.

The `assembly` object references reusable 3D template components, not raw generated meshes. This keeps AI output executable:

1. `components` describe facade, roof, entrance, signage, connector, and platform-cover parts
2. `transform` and `dimensions` place them in station-local coordinates
3. `anchors` define rail, road, pedestrian, metro, bus, and service connection points
4. `collision` and `lod` describe how the package builder should create runtime-friendly geometry

This is the contract that lets the backend assemble a metro station shell before game-specific code binds transport behavior.
