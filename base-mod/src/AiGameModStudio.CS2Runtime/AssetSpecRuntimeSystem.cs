#if CITIES_SKYLINES_2
using System;
using System.IO;
using AiGameModStudio.BaseMod.Core;
using Game;

namespace AiGameModStudio.CS2Runtime;

public partial class AssetSpecRuntimeSystem : GameSystemBase
{
    private const string SpecFileName = "active-asset.json";
    private DateTime _lastLoadedAtUtc = DateTime.MinValue;

    protected override void OnCreate()
    {
        base.OnCreate();
        Mod.Log.Info("Asset Spec runtime system created.");
        TryLoadActiveSpec();
    }

    protected override void OnUpdate()
    {
        // MVP: poll occasionally during development. Replace with a file watcher or explicit UI action later.
        if ((DateTime.UtcNow - _lastLoadedAtUtc).TotalSeconds < 10)
        {
            return;
        }

        TryLoadActiveSpec();
    }

    private void TryLoadActiveSpec()
    {
        _lastLoadedAtUtc = DateTime.UtcNow;

        try
        {
            var specPath = GetSpecPath();
            if (!File.Exists(specPath))
            {
                Mod.Log.Info($"No active Asset Spec found at {specPath}.");
                return;
            }

            var spec = AssetSpecLoader.LoadFromFile(specPath);
            var report = new AssetSpecValidator().Validate(spec);

            foreach (var issue in report.Issues)
            {
                Mod.Log.Info($"{issue.Severity}: {issue.Code} at {issue.Path}: {issue.Message}");
            }

            if (report.HasErrors)
            {
                Mod.Log.Error("Asset Spec has validation errors; skipping runtime plan.");
                return;
            }

            var plan = new StationTemplateBuilder().Build(spec);
            Mod.Log.Info($"Loaded Asset Spec '{plan.DisplayName}' with {plan.ModuleInstances.Count} module instances.");

            // TODO: Map RuntimeModuleInstance values to CS2 prefabs/components once the official template project
            // exposes the correct prefab references and instantiation API.
        }
        catch (Exception exception)
        {
            Mod.Log.Error($"Failed to load active Asset Spec: {exception}");
        }
    }

    private static string GetSpecPath()
    {
        var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        return Path.Combine(localAppData, "Colossal Order", "Cities Skylines II", "ModsData", "AiGameModStudio", SpecFileName);
    }
}
#endif
