from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional, Union

from model_providers import ChatMessage, ChatRequest


KNOWN_MODULES = [
    "station.platform.island.small",
    "station.platform.island.medium",
    "station.platform.side.small",
    "station.concourse.basic",
    "station.concourse.glass_hall",
    "station.entrance.single",
    "station.entrance.corner",
    "station.decor.canopy",
    "station.decor.signage",
]

KNOWN_ASSEMBLY_COMPONENTS = [
    "shell.facade.glass_grid",
    "shell.facade.concrete_core",
    "shell.facade.painted_metal_band",
    "roof.glass_canopy",
    "roof.steel_ribs",
    "entrance.urban_corner_shell",
    "platform.canopy.steel",
    "signage.lightbox_bilingual",
    "connector.pedestrian_bridge",
    "connector.metro_subsurface_stub",
]


ORCHESTRATOR_RESPONSE_SHAPE = {
    "status": "ready | needs_clarification",
    "questions": [
        {
            "id": "short_snake_case",
            "question": "Question to ask the user",
            "reason": "Why this answer is needed",
        }
    ],
    "asset_spec": "Asset Spec object when status is ready, otherwise null",
    "design_explanation": "Short user-facing explanation",
    "template_rationale": ["Why these modules and constraints were selected"],
}


def build_orchestrator_request(
    user_prompt: str,
    schema_path: Union[str, Path],
    model: Optional[str] = None,
    user_constraints: Optional[Mapping[str, Any]] = None,
    existing_answers: Optional[Mapping[str, Any]] = None,
) -> ChatRequest:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    prompt_context = {
        "user_prompt": user_prompt,
        "user_constraints": dict(user_constraints or {}),
        "existing_answers": dict(existing_answers or {}),
        "known_modules": KNOWN_MODULES,
        "known_assembly_components": KNOWN_ASSEMBLY_COMPONENTS,
        "asset_spec_schema": schema,
        "required_response_shape": ORCHESTRATOR_RESPONSE_SHAPE,
    }

    return ChatRequest(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            ChatMessage(
                role="system",
                content=(
                    "You are the AI Game Mod Studio Asset Spec orchestrator. "
                    "Your job is to turn a user's natural-language request into "
                    "an Asset Spec v0.1 for a Cities: Skylines II train station. "
                    "Choose only known module IDs. Use fictional branding for "
                    "real-world inspired designs. Include an assembly object "
                    "when the user asks for a buildable station shell, facade, "
                    "3D layout, or game-ready placement. The assembly object "
                    "must describe template components, transforms, dimensions, "
                    "facades, and connection anchors instead of inventing meshes. "
                    "If the request lacks enough "
                    "information to make a playable station, ask at most three "
                    "clarifying questions. Return only JSON, no Markdown."
                ),
            ),
            ChatMessage(
                role="user",
                content=json.dumps(prompt_context, ensure_ascii=False),
            ),
        ],
    )
