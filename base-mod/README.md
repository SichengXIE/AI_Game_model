# Base Mod Proof of Concept

This folder validates the first technical assumption for the product:

1. Read an external `Asset Spec` JSON file.
2. Validate that it describes a supported MVP asset.
3. Convert it into a deterministic station runtime plan.
4. Hand that runtime plan to a Cities: Skylines II code mod for in-game instantiation.

## Current Scope

The MVP supports only one asset type:

- `train_station`

Supported configurable fields:

- display name
- footprint width and length
- platform modules
- entrance modules
- rail tracks
- road access
- pedestrian entries
- theme, regional inspiration, materials, sign languages, and colors

## Local Probe

The local probe validates the config and prints the runtime plan that the CS2 adapter will consume.

```bash
dotnet run --project base-mod/src/AiGameModStudio.SpecProbe -- examples/asset-specs/minimal-harbor-station.json
```

Expected result:

- exit code `0`
- no validation errors
- JSON output containing `module_instances`

## CS2 Integration

The actual in-game runtime must be created from the official Cities: Skylines II code-mod template. After that template exists, copy the adapter files from:

```text
base-mod/src/AiGameModStudio.CS2Runtime/
```

The adapter currently loads this file:

```text
<LocalApplicationData>/Colossal Order/Cities Skylines II/ModsData/AiGameModStudio/active-asset.json
```

## Important Boundary

This proof of concept does not yet generate high-fidelity custom meshes. It validates the safer first step: external spec loading, deterministic validation, and a runtime plan that can later map to CS2 prefabs, Editor-created assets, or template modules.
