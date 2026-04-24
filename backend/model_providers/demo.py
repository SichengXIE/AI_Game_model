from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import ChatRequest, ChatResponse


DEMO_PROVIDER_ID = "local-demo"
DEMO_MODEL = "template-demo-v0.1"


class LocalDemoAssetSpecClient:
    def complete(self, request: ChatRequest) -> ChatResponse:
        prompt_context = _extract_prompt_context(request)
        user_prompt = str(prompt_context.get("user_prompt", ""))
        asset_spec = _build_demo_asset_spec(user_prompt)
        content = json.dumps(
            {
                "status": "ready",
                "questions": [],
                "asset_spec": asset_spec,
                "design_explanation": (
                    "Local demo mode generated a template-based station Asset Spec without "
                    "calling an external model provider."
                ),
                "template_rationale": [
                    "Uses known station modules so Package Builder and Base Mod validation can run.",
                    "Includes assembly components, anchors, colors, materials, and runtime constraints.",
                    "Keeps branding fictional for real-world inspired station styles.",
                ],
            },
            ensure_ascii=False,
        )
        return ChatResponse(
            provider_id=DEMO_PROVIDER_ID,
            model=request.model or DEMO_MODEL,
            content=content,
            raw={"demo": True},
        )


def _extract_prompt_context(request: ChatRequest) -> Mapping[str, Any]:
    for message in reversed(request.messages):
        if message.role == "user":
            try:
                data = json.loads(message.content)
            except json.JSONDecodeError:
                return {}
            return data if isinstance(data, Mapping) else {}
    return {}


def _build_demo_asset_spec(user_prompt: str) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    spec_path = repo_root / "examples" / "asset-specs" / "hk-mtr-interchange-station.json"
    asset_spec = copy.deepcopy(json.loads(spec_path.read_text(encoding="utf-8")))

    normalized_prompt = user_prompt.lower()
    asset_spec["source_intent"]["user_prompt"] = user_prompt or asset_spec["source_intent"]["user_prompt"]
    asset_spec["metadata"]["asset_id"] = "local-demo-template-station"
    asset_spec["metadata"]["tags"] = ["local-demo", "template-based", "web-mvp"]

    if any(keyword in normalized_prompt for keyword in ("suburban", "compact", "紧凑", "郊区")):
        _apply_compact_station_variant(asset_spec)
    elif any(keyword in normalized_prompt for keyword in ("airport", "机场")):
        asset_spec["title"] = "Airport Rail Interchange Demo"
        asset_spec["description"] = (
            "A rail station concept for an airport district, built from the current station "
            "template set until airport-specific modules are added."
        )
        asset_spec["style"]["regional_inspiration"] = "airport_district"
        asset_spec["decor"]["color_palette"] = ["#1D4ED8", "#E6E6E6", "#333333", "#FFFFFF"]
    elif any(keyword in normalized_prompt for keyword in ("modern", "现代")):
        asset_spec["title"] = "Modern Glass Transit Station Demo"
        asset_spec["description"] = (
            "A modern glass transit station assembled from template modules with clear signage "
            "and a mid-sized footprint."
        )

    return asset_spec


def _apply_compact_station_variant(asset_spec: dict[str, Any]) -> None:
    asset_spec["title"] = "Compact Suburban Station Demo"
    asset_spec["description"] = (
        "A compact suburban station assembled from side platform, basic concourse, and single "
        "entrance templates."
    )
    asset_spec["subtype"] = "small_station"
    asset_spec["footprint"]["width"] = 40
    asset_spec["footprint"]["length"] = 96
    asset_spec["modules"] = [
        {
            "module_id": "station.platform.side.small",
            "count": 2,
            "role": "platform",
            "placement": {"zone": "track_core", "priority": 100},
            "parameters": {"canopy": True, "platform_edge_color": "#2F6F4E"},
        },
        {
            "module_id": "station.concourse.basic",
            "count": 1,
            "role": "concourse",
            "placement": {"zone": "concourse_center", "priority": 80},
            "parameters": {"ticket_hall": False},
        },
        {
            "module_id": "station.entrance.single",
            "count": 1,
            "role": "entrance",
            "placement": {"zone": "street_edge", "priority": 70},
            "parameters": {"entrance_type": "suburban_single", "covered": True},
        },
    ]
    asset_spec["connections"]["rail_tracks"] = 2
    asset_spec["connections"]["road_access"] = 1
    asset_spec["connections"]["pedestrian_entries"] = 1
    asset_spec["decor"]["color_palette"] = ["#2F6F4E", "#E7E0D0", "#333333", "#FFFFFF"]
