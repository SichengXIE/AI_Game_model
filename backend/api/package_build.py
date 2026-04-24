from __future__ import annotations

import base64
from dataclasses import asdict
from typing import Any, Mapping, Optional

from orchestrator.contracts import ValidationIssue
from package_builder import PackageBuilder, PackageBuildError

from .spec_generation import ApiError


class PackageBuildService:
    def __init__(self, builder: Optional[PackageBuilder] = None):
        self.builder = builder or PackageBuilder()

    def build(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        asset_spec = payload.get("asset_spec")
        if not isinstance(asset_spec, Mapping):
            raise ApiError(400, "missing_asset_spec", "Request body must include asset_spec object.")

        try:
            package = self.builder.build(asset_spec)
        except PackageBuildError as error:
            return {
                "status": "invalid",
                "error": {"code": error.code, "message": error.message},
                "validation_issues": [
                    asdict(issue) if isinstance(issue, ValidationIssue) else str(issue)
                    for issue in error.issues
                ],
            }

        return {
            "status": "ready",
            "package_id": package.package_id,
            "filename": package.filename,
            "content_type": "application/zip",
            "encoding": "base64",
            "zip_base64": base64.b64encode(package.zip_bytes).decode("ascii"),
            "manifest": package.manifest,
            "preview": package.preview,
            "files": package.manifest.get("files", []),
        }
