# MVP Stage Roadmap

This document tracks the execution path for the first playable loop:

```text
Web prompt -> Asset Spec -> Package Builder -> Base Mod runtime load
```

## Stage 1: Web MVP Loop

Status: in progress, usable for local demos.

Implemented:

1. Static Web interface in `frontend/`.
2. `GET /api/providers` for model selection metadata.
3. `POST /api/specs/generate` for prompt-to-Asset-Spec conversion.
4. `POST /api/packages/build` for zip package generation.
5. `local-demo` provider for API-key-free demos and regression tests.

Acceptance criteria:

1. A beginner user opens the web page and enters a natural-language station prompt.
2. The default `local-demo` provider completes the flow without external API keys.
3. A real provider such as `qwen-hk`, `gemini`, `openai`, or `doubao-ark` can be selected when its API key is configured.
4. The browser receives a downloadable zip containing `active-asset.json`, `manifest.json`, `preview.json`, and `README.md`.
5. `active-asset.json` validates against Asset Spec v0.1 and can be consumed by Base Mod validation tools.

Next implementation tasks:

1. Add a one-click integration test that starts the API server and exercises the browser flow through HTTP.
2. Add a frontend progress state for `needs_clarification` responses.
3. Add an editable Asset Spec panel so advanced users can inspect and patch fields before packaging.
4. Add a package preview pane that summarizes footprint, modules, anchors, colors, and runtime limits.

## Stage 2: CS2 Base Mod Runtime

Status: external data folder, runtime status files, and hot reload core exist; real CS2 ECS/PrefabSystem binding still needs an official mod-template integration pass.

Implemented:

1. C# Asset Spec models.
2. C# Asset Spec loader and validator.
3. C# station runtime plan builder.
4. SpecProbe command-line validation project.
5. External `active-asset.json` data directory contract.
6. Runtime status log and latest status snapshot.
7. File watcher plus polling fallback for hot reload.
8. CS2 runtime adapter wired to the shared Core runtime service.

Acceptance criteria:

1. Base Mod reads an external `active-asset.json` from a deterministic data folder.
2. Base Mod validates the spec and reports structured errors.
3. Base Mod maps modules and assembly components into a runtime station plan.
4. Base Mod binds the runtime plan to CS2 ECS and PrefabSystem APIs.
5. A generated station appears in game with expected footprint, name, anchors, color/material overrides, and basic collision/LOD behavior.

Next implementation tasks:

1. Copy `AiGameModStudio.CS2Runtime` into an official CS2 code-mod template and verify the watcher in game.
2. Add an in-game status UI or options panel that reads `runtime-status.json`.
3. Replace the runtime-plan placeholder with real ECS/PrefabSystem integration after testing inside the official mod template.
4. Add failure-mode fixtures for missing modules, invalid anchors, and unsupported assembly components.

## Stage 3: Asset Pipeline Alignment

Status: package format is internal runtime input, not yet an official CS2 asset package.

Current package contract:

1. `active-asset.json`: Base Mod runtime input.
2. `manifest.json`: package metadata and file roles.
3. `preview.json`: frontend/user preview metadata.
4. `README.md`: user installation notes.

Acceptance criteria:

1. The internal package explicitly separates Base Mod runtime packages from official CS2 upload/share packages.
2. Template component metadata can express color variations, emission intent, collision strategy, and LOD strategy.
3. Asset Pipeline constraints are documented as validation rules before the builder emits official-package-compatible outputs.
4. Generated packages fail fast when a requested mesh/material/emission feature has no supported template binding.

Next implementation tasks:

1. Add schema fields for `material_slots`, `color_variations`, and `emission` once the Base Mod binding contract is confirmed.
2. Add Package Builder validation that rejects unsupported mesh or official-package claims.
3. Add a separate exporter interface for future official CS2 asset package output.

## Stage 4: Advanced Local App Preparation

Status: deferred until Stage 1 and Stage 2 are stable.

Acceptance criteria:

1. Advanced users can generate, inspect, edit, and repackage Asset Spec locally.
2. The app can locate the CS2 user/mod data directory.
3. The app can install `active-asset.json` packages and Base Mod files into the expected folders.
4. The app exposes logs, settings, developer-mode guidance, and package validation errors.

Next implementation tasks:

1. Decide desktop shell: Python desktop wrapper, C# desktop app, or lightweight webview around the existing frontend.
2. Design a local package library with installed/draft/error states.
3. Add a settings editor that maps directly to Base Mod config files.
4. Add log collection from the Base Mod runtime folder.
