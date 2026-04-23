# CS2 Runtime Adapter

This folder contains the game-facing runtime skeleton for the Base Mod.

The files are wrapped in `#if CITIES_SKYLINES_2` because they depend on the official Cities: Skylines II code-mod template and game assemblies. Do not treat this folder as a standalone buildable project yet.

Integration steps:

1. Open Cities: Skylines II and install/update the official code-mod toolchain.
2. Create a new code mod from the official template in Visual Studio or Rider.
3. Add a reference to `AiGameModStudio.BaseMod.Core`.
4. Copy `Mod.cs` and `AssetSpecRuntimeSystem.cs` into the generated CS2 mod project.
5. Define the `CITIES_SKYLINES_2` compilation symbol in that project.
6. Build through the official template so CS2 post-processing and deployment steps run.

The first in-game test is successful when the game log shows that `active-asset.json` was found, validated, and converted into a station runtime plan.
