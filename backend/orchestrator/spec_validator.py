from __future__ import annotations

import re
from typing import Any, Mapping

from .contracts import ValidationIssue
from .prompting import KNOWN_ASSEMBLY_COMPONENTS, KNOWN_MODULES


HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def validate_asset_spec_contract(spec: Mapping[str, Any]) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []

    _expect(spec.get("spec_version") == "0.1", issues, "invalid_spec_version", "spec_version must be 0.1.", "$.spec_version")
    _expect(spec.get("game") == "cities_skylines_2", issues, "invalid_game", "game must be cities_skylines_2.", "$.game")
    _expect(spec.get("asset_type") == "train_station", issues, "invalid_asset_type", "asset_type must be train_station.", "$.asset_type")
    _expect(isinstance(spec.get("title"), str) and bool(spec.get("title")), issues, "missing_title", "title is required.", "$.title")

    style = spec.get("style")
    if isinstance(style, Mapping):
        _expect(isinstance(style.get("theme"), str) and bool(style.get("theme")), issues, "missing_theme", "style.theme is required.", "$.style.theme")
        _expect(isinstance(style.get("regional_inspiration"), str) and bool(style.get("regional_inspiration")), issues, "missing_regional_inspiration", "style.regional_inspiration is required.", "$.style.regional_inspiration")
        _expect(_is_non_empty_list(style.get("materials")), issues, "missing_materials", "style.materials must be a non-empty list.", "$.style.materials")
    else:
        issues.append(ValidationIssue("missing_style", "style object is required.", "$.style"))

    footprint = spec.get("footprint")
    if isinstance(footprint, Mapping):
        _expect(_int_between(footprint.get("width"), 1, 256), issues, "invalid_width", "footprint.width must be between 1 and 256.", "$.footprint.width")
        _expect(_int_between(footprint.get("length"), 1, 512), issues, "invalid_length", "footprint.length must be between 1 and 512.", "$.footprint.length")
        _expect(footprint.get("height_class") in {"lowrise", "midrise", "tall_hall"}, issues, "invalid_height_class", "footprint.height_class is invalid.", "$.footprint.height_class")
    else:
        issues.append(ValidationIssue("missing_footprint", "footprint object is required.", "$.footprint"))

    modules = spec.get("modules")
    if isinstance(modules, list) and modules:
        _validate_modules(modules, issues)
    else:
        issues.append(ValidationIssue("missing_modules", "modules must be a non-empty list.", "$.modules"))

    assembly = spec.get("assembly")
    if assembly is not None:
        if isinstance(assembly, Mapping):
            _validate_assembly(assembly, issues)
        else:
            issues.append(ValidationIssue("invalid_assembly", "assembly must be an object.", "$.assembly"))

    connections = spec.get("connections")
    if isinstance(connections, Mapping):
        _expect(_int_between(connections.get("rail_tracks"), 1, 12), issues, "invalid_rail_tracks", "connections.rail_tracks must be between 1 and 12.", "$.connections.rail_tracks")
        _expect(_int_between(connections.get("road_access"), 0, 8), issues, "invalid_road_access", "connections.road_access must be between 0 and 8.", "$.connections.road_access")
        _expect(_int_between(connections.get("pedestrian_entries"), 1, 16), issues, "invalid_pedestrian_entries", "connections.pedestrian_entries must be between 1 and 16.", "$.connections.pedestrian_entries")
    else:
        issues.append(ValidationIssue("missing_connections", "connections object is required.", "$.connections"))

    decor = spec.get("decor")
    if isinstance(decor, Mapping):
        _expect(_is_non_empty_list(decor.get("sign_language")), issues, "missing_sign_language", "decor.sign_language must be a non-empty list.", "$.decor.sign_language")
        colors = decor.get("color_palette")
        _expect(_is_non_empty_list(colors), issues, "missing_color_palette", "decor.color_palette must be a non-empty list.", "$.decor.color_palette")
        if isinstance(colors, list):
            for index, color in enumerate(colors):
                _expect(isinstance(color, str) and bool(HEX_COLOR.match(color)), issues, "invalid_color", "color_palette entries must use #RRGGBB.", f"$.decor.color_palette[{index}]")
    else:
        issues.append(ValidationIssue("missing_decor", "decor object is required.", "$.decor"))

    runtime = spec.get("runtime_constraints")
    if isinstance(runtime, Mapping):
        _expect(runtime.get("template_only") is True, issues, "template_only_required", "runtime_constraints.template_only must be true.", "$.runtime_constraints.template_only")
        _expect(runtime.get("requires_base_mod") is True, issues, "base_mod_required", "runtime_constraints.requires_base_mod must be true.", "$.runtime_constraints.requires_base_mod")
        _expect(isinstance(runtime.get("base_mod_min_version"), str) and bool(runtime.get("base_mod_min_version")), issues, "missing_base_mod_version", "base_mod_min_version is required.", "$.runtime_constraints.base_mod_min_version")
    else:
        issues.append(ValidationIssue("missing_runtime_constraints", "runtime_constraints object is required.", "$.runtime_constraints"))

    return tuple(issues)


def _validate_modules(modules: list[Any], issues: list[ValidationIssue]) -> None:
    has_platform = False
    has_entrance = False

    for index, module in enumerate(modules):
        path = f"$.modules[{index}]"
        if not isinstance(module, Mapping):
            issues.append(ValidationIssue("invalid_module", "module must be an object.", path))
            continue

        module_id = module.get("module_id")
        count = module.get("count")
        if module_id not in KNOWN_MODULES:
            issues.append(ValidationIssue("unknown_module_id", f"Unknown module_id: {module_id}", f"{path}.module_id"))
        if not _int_between(count, 1, 12):
            issues.append(ValidationIssue("invalid_module_count", "module count must be between 1 and 12.", f"{path}.count"))

        if isinstance(module_id, str) and ".platform." in module_id:
            has_platform = True
        if isinstance(module_id, str) and ".entrance." in module_id:
            has_entrance = True

    _expect(has_platform, issues, "missing_platform", "At least one platform module is required.", "$.modules")
    _expect(has_entrance, issues, "missing_entrance", "At least one entrance module is required.", "$.modules")


def _validate_assembly(assembly: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    components = assembly.get("components")
    anchors = assembly.get("anchors")

    if not isinstance(components, list) or not components:
        issues.append(ValidationIssue("missing_assembly_components", "assembly.components must be a non-empty list.", "$.assembly.components"))
    else:
        for index, component in enumerate(components):
            path = f"$.assembly.components[{index}]"
            if not isinstance(component, Mapping):
                issues.append(ValidationIssue("invalid_assembly_component", "assembly component must be an object.", path))
                continue
            component_id = component.get("component_id")
            if component_id not in KNOWN_ASSEMBLY_COMPONENTS:
                issues.append(ValidationIssue("unknown_component_id", f"Unknown component_id: {component_id}", f"{path}.component_id"))
            if not isinstance(component.get("instance_id"), str) or not component.get("instance_id"):
                issues.append(ValidationIssue("missing_component_instance_id", "assembly component instance_id is required.", f"{path}.instance_id"))
            if not isinstance(component.get("transform"), Mapping):
                issues.append(ValidationIssue("missing_component_transform", "assembly component transform is required.", f"{path}.transform"))
            if not isinstance(component.get("dimensions"), Mapping):
                issues.append(ValidationIssue("missing_component_dimensions", "assembly component dimensions are required.", f"{path}.dimensions"))

    if not isinstance(anchors, list) or not anchors:
        issues.append(ValidationIssue("missing_assembly_anchors", "assembly.anchors must be a non-empty list.", "$.assembly.anchors"))
    else:
        for index, anchor in enumerate(anchors):
            path = f"$.assembly.anchors[{index}]"
            if not isinstance(anchor, Mapping):
                issues.append(ValidationIssue("invalid_assembly_anchor", "assembly anchor must be an object.", path))
                continue
            if not isinstance(anchor.get("anchor_id"), str) or not anchor.get("anchor_id"):
                issues.append(ValidationIssue("missing_anchor_id", "assembly anchor_id is required.", f"{path}.anchor_id"))
            if anchor.get("type") not in {"rail_track", "road_access", "pedestrian_entry", "metro_transfer", "bus_stop", "service_access"}:
                issues.append(ValidationIssue("invalid_anchor_type", "assembly anchor type is invalid.", f"{path}.type"))
            if not isinstance(anchor.get("position"), Mapping):
                issues.append(ValidationIssue("missing_anchor_position", "assembly anchor position is required.", f"{path}.position"))


def _expect(condition: bool, issues: list[ValidationIssue], code: str, message: str, path: str) -> None:
    if not condition:
        issues.append(ValidationIssue(code=code, message=message, path=path))


def _is_non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def _int_between(value: Any, minimum: int, maximum: int) -> bool:
    return isinstance(value, int) and minimum <= value <= maximum
