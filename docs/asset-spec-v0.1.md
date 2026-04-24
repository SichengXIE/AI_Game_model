# Asset Spec v0.1

`Asset Spec` 是 AI 和游戏运行时之间的中间语言。AI 不直接生成 DLL、Prefab 或游戏文件，而是生成一份可校验的结构化蓝图，再由校验器、模板库、打包器和 CS2 `Base Mod` 处理。

## 1. 设计边界

v0.1 只服务一个可执行目标：

1. 游戏：`cities_skylines_2`
2. 资产类型：`train_station`
3. 生成方式：模板化模块拼装
4. 运行方式：需要 `Base Mod`
5. 输出对象：站点 runtime plan 或 `active-asset.json`

“港铁风格的换乘站”在 v0.1 中仍然是：

```json
{
  "asset_type": "train_station",
  "subtype": "interchange_station"
}
```

原因是当前 Base Mod 只验证站点类资产。`subtype` 和 `style` 负责表达“换乘站”和“港铁风格”，避免过早扩大 runtime 类型。

## 2. 字段分层

v0.1 分为两层字段：

1. 执行核心字段：Base Mod 当前必须能读取和执行
2. 设计语义字段：AI、前端预览、模板匹配和后续生成器使用

执行核心字段包括：

1. `spec_version`
2. `game`
3. `asset_type`
4. `title`
5. `style.theme`
6. `style.regional_inspiration`
7. `style.materials`
8. `footprint.width`
9. `footprint.length`
10. `footprint.height_class`
11. `modules[].module_id`
12. `modules[].count`
13. `connections.rail_tracks`
14. `connections.road_access`
15. `connections.pedestrian_entries`
16. `decor.sign_language`
17. `decor.color_palette`
18. `runtime_constraints.template_only`
19. `runtime_constraints.requires_base_mod`
20. `runtime_constraints.base_mod_min_version`

设计语义字段包括：

1. `metadata`
2. `source_intent`
3. `subtype`
4. `description`
5. `style.architectural_language`
6. `style.lighting`
7. `style.reference_notes`
8. `footprint.orientation`
9. `footprint.platform_length_class`
10. `modules[].role`
11. `modules[].variant`
12. `modules[].placement`
13. `modules[].parameters`
14. `connections.transit_modes`
15. `connections.road_access_type`
16. `connections.pedestrian_network`
17. `decor.signage_style`
18. `decor.logo_policy`
19. `decor.surface_patterns`
20. `preview_hints`
21. `compatibility`

## 3. Required Contract

Every v0.1 spec must satisfy:

```json
{
  "spec_version": "0.1",
  "game": "cities_skylines_2",
  "asset_type": "train_station",
  "title": "Human-readable asset name",
  "style": {},
  "footprint": {},
  "modules": [],
  "connections": {},
  "decor": {},
  "runtime_constraints": {}
}
```

The canonical JSON Schema is:

```text
schemas/asset-spec.schema.json
```

## 4. Asset Identity

`title` is the user-facing name. Keep it short enough for in-game UI.

`metadata.asset_id` is a stable machine identifier. Use lowercase slugs:

```json
{
  "metadata": {
    "asset_id": "hk-mtr-glass-interchange",
    "author": "AI Game Mod Studio",
    "tags": ["hong-kong", "mtr-inspired", "interchange"]
  }
}
```

## 5. Style

`style` describes what the asset should look like. It does not bind directly to copyrighted logos or protected brand assets.

For real-world inspiration, use `regional_inspiration` and `reference_notes`:

```json
{
  "style": {
    "theme": "modern_transit",
    "regional_inspiration": "hong_kong",
    "architectural_language": ["dense urban station", "glass concourse", "clear wayfinding"],
    "materials": ["glass", "steel", "concrete", "painted_metal"],
    "lighting": "bright_platforms",
    "reference_notes": ["MTR-inspired red accent color", "bilingual wayfinding"]
  }
}
```

## 6. Footprint

`footprint` controls the asset envelope used by validators and layout planners.

The MVP should stay inside:

1. `width <= 256`
2. `length <= 512`
3. `height_class` in `lowrise`, `midrise`, `tall_hall`

For station assets, `orientation` should usually be `track_parallel`.

## 7. Modules

`modules` is the executable assembly list. AI can only use module IDs listed in the schema and template library.

Supported v0.1 modules:

1. `station.platform.island.small`
2. `station.platform.island.medium`
3. `station.platform.side.small`
4. `station.concourse.basic`
5. `station.concourse.glass_hall`
6. `station.entrance.single`
7. `station.entrance.corner`
8. `station.decor.canopy`
9. `station.decor.signage`

Each module must include:

```json
{
  "module_id": "station.platform.island.medium",
  "count": 2
}
```

Optional fields such as `role`, `placement`, and `parameters` help the template matcher and future runtime place modules more intelligently.

## 8. Connections

`connections` gives both a simple numeric summary and optional semantic hints.

The current C# probe uses:

1. `rail_tracks`
2. `road_access`
3. `pedestrian_entries`

Future runtime and preview systems may also use:

1. `transit_modes`
2. `road_access_type`
3. `pedestrian_network`

## 9. Decor

`decor` defines sign languages, colors, and surface treatment.

For Hong Kong-inspired stations, use fictional signs and palettes unless the user provides licensed assets:

```json
{
  "decor": {
    "sign_language": ["zh-HK", "en"],
    "color_palette": ["#C8102E", "#E6E6E6", "#333333"],
    "signage_style": "mtr_inspired",
    "logo_policy": "fictional_only",
    "surface_patterns": ["platform_stripes", "glass_mullions"]
  }
}
```

## 10. Runtime Constraints

v0.1 must remain template-based:

```json
{
  "runtime_constraints": {
    "template_only": true,
    "requires_base_mod": true,
    "base_mod_min_version": "0.1.0",
    "allowed_runtime": "cs2_base_mod",
    "max_module_instances": 64
  }
}
```

The validator should reject specs that require arbitrary C# generation, direct DLL output, or unsupported prefab creation.

## 11. AI Output Rules

When the AI receives a user request, it should:

1. Generate only valid JSON
2. Use `asset_type: train_station`
3. Use `subtype` to express station class
4. Use only known module IDs
5. Keep dimensions within schema limits
6. Include at least one platform module
7. Include at least one entrance module
8. Use `decor.logo_policy: fictional_only` for real-world inspired assets
9. Put uncertainty into `source_intent.avoid` or `compatibility.known_limits`
10. Never invent module IDs

## 12. Example User Mapping

User says:

```text
我想做一个港铁风格的换乘站，有两个岛式站台、玻璃大厅、双语标识和红白灰配色。
```

AI should generate:

```text
examples/asset-specs/hk-mtr-interchange-station.json
```

The output is still a structured blueprint. It is not a compiled mod and not a high-fidelity 3D model.
