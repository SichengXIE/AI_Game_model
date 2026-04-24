from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Mapping

from orchestrator.spec_validator import validate_asset_spec_contract


class PackageBuildError(Exception):
    def __init__(self, code: str, message: str, issues: tuple[Any, ...] = ()):
        super().__init__(message)
        self.code = code
        self.message = message
        self.issues = issues


@dataclass(frozen=True)
class AssetPackage:
    package_id: str
    filename: str
    manifest: Mapping[str, Any]
    preview: Mapping[str, Any]
    readme: str
    zip_bytes: bytes

    @property
    def file_count(self) -> int:
        return len(self.manifest.get("files", []))


class PackageBuilder:
    def build(self, asset_spec: Mapping[str, Any]) -> AssetPackage:
        issues = validate_asset_spec_contract(asset_spec)
        if issues:
            raise PackageBuildError(
                code="invalid_asset_spec",
                message="Asset Spec failed package validation.",
                issues=issues,
            )

        active_asset = _to_pretty_json(asset_spec)
        package_id = _stable_package_id(asset_spec, active_asset)
        manifest = _build_manifest(asset_spec, package_id, active_asset)
        preview = _build_preview(asset_spec)
        readme = _build_readme(asset_spec, package_id)
        zip_bytes = _build_zip(
            {
                "active-asset.json": active_asset,
                "manifest.json": _to_pretty_json(manifest),
                "preview.json": _to_pretty_json(preview),
                "README.md": readme,
            }
        )

        return AssetPackage(
            package_id=package_id,
            filename=f"{package_id}.zip",
            manifest=manifest,
            preview=preview,
            readme=readme,
            zip_bytes=zip_bytes,
        )


def _stable_package_id(asset_spec: Mapping[str, Any], active_asset_json: str) -> str:
    metadata = asset_spec.get("metadata")
    asset_id = ""
    if isinstance(metadata, Mapping):
        asset_id = str(metadata.get("asset_id", ""))

    if not asset_id:
        title = str(asset_spec.get("title", "untitled-station"))
        asset_id = _slugify(title)

    digest = hashlib.sha256(active_asset_json.encode("utf-8")).hexdigest()[:10]
    return f"{_slugify(asset_id)}-{digest}"


def _build_manifest(
    asset_spec: Mapping[str, Any],
    package_id: str,
    active_asset_json: str,
) -> dict[str, Any]:
    assembly = asset_spec.get("assembly")
    components = []
    anchors = []
    if isinstance(assembly, Mapping):
        components = list(assembly.get("components", []))
        anchors = list(assembly.get("anchors", []))

    return {
        "manifest_version": "0.1",
        "package_id": package_id,
        "asset_title": asset_spec.get("title"),
        "asset_type": asset_spec.get("asset_type"),
        "spec_version": asset_spec.get("spec_version"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requires_base_mod": True,
        "base_mod_min_version": asset_spec.get("runtime_constraints", {}).get("base_mod_min_version"),
        "active_asset_sha256": hashlib.sha256(active_asset_json.encode("utf-8")).hexdigest(),
        "assembly": {
            "component_count": len(components),
            "anchor_count": len(anchors),
            "component_ids": sorted(
                {
                    str(component.get("component_id"))
                    for component in components
                    if isinstance(component, Mapping)
                }
            ),
        },
        "files": [
            {"path": "active-asset.json", "role": "base_mod_input"},
            {"path": "manifest.json", "role": "package_manifest"},
            {"path": "preview.json", "role": "preview_metadata"},
            {"path": "README.md", "role": "user_instructions"},
        ],
    }


def _build_preview(asset_spec: Mapping[str, Any]) -> dict[str, Any]:
    modules = asset_spec.get("modules", [])
    assembly = asset_spec.get("assembly", {})
    components = assembly.get("components", []) if isinstance(assembly, Mapping) else []
    anchors = assembly.get("anchors", []) if isinstance(assembly, Mapping) else []

    return {
        "title": asset_spec.get("title"),
        "description": asset_spec.get("description", ""),
        "style": asset_spec.get("style", {}),
        "footprint": asset_spec.get("footprint", {}),
        "connections": asset_spec.get("connections", {}),
        "decor": asset_spec.get("decor", {}),
        "module_summary": [
            {
                "module_id": module.get("module_id"),
                "count": module.get("count"),
                "role": module.get("role"),
            }
            for module in modules
            if isinstance(module, Mapping)
        ],
        "assembly_summary": {
            "components": [
                {
                    "component_id": component.get("component_id"),
                    "instance_id": component.get("instance_id"),
                    "purpose": component.get("purpose"),
                    "dimensions": component.get("dimensions"),
                }
                for component in components
                if isinstance(component, Mapping)
            ],
            "anchors": [
                {
                    "anchor_id": anchor.get("anchor_id"),
                    "type": anchor.get("type"),
                    "position": anchor.get("position"),
                }
                for anchor in anchors
                if isinstance(anchor, Mapping)
            ],
        },
    }


def _build_readme(asset_spec: Mapping[str, Any], package_id: str) -> str:
    title = str(asset_spec.get("title", "Untitled Station"))
    description = str(asset_spec.get("description", "Generated station asset package."))
    base_mod_version = asset_spec.get("runtime_constraints", {}).get("base_mod_min_version", "0.1.0")

    return "\n".join(
        [
            f"# {title}",
            "",
            description,
            "",
            f"Package ID: `{package_id}`",
            "",
            "## Install",
            "",
            "1. Install the AI Game Mod Studio CS2 Base Mod.",
            "2. Copy `active-asset.json` into the Base Mod data folder.",
            "3. Start Cities: Skylines II and load the Base Mod.",
            "",
            "## Requirements",
            "",
            f"- Base Mod minimum version: `{base_mod_version}`",
            "- This package uses template-based geometry and assembly metadata.",
            "- Real-world logos are not included unless explicitly provided by the user.",
            "",
        ]
    )


def _build_zip(files: Mapping[str, str]) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, content in files.items():
            archive.writestr(path, content)
    return buffer.getvalue()


def _to_pretty_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _slugify(value: str) -> str:
    chars = [
        character.lower() if character.isascii() and character.isalnum() else "-"
        for character in value.strip()
    ]
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "untitled-station"
