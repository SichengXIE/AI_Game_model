namespace AiGameModStudio.BaseMod.Core;

public sealed class StationTemplateBuilder
{
    public StationRuntimePlan Build(AssetSpec spec)
    {
        var report = new AssetSpecValidator().Validate(spec);
        if (report.HasErrors)
        {
            throw new InvalidOperationException("Cannot build runtime plan from an invalid Asset Spec.");
        }

        return new StationRuntimePlan
        {
            AssetName = ToStableAssetName(spec.Title),
            DisplayName = spec.Title,
            Footprint = spec.Footprint,
            Connections = spec.Connections,
            Style = spec.Style,
            ColorPalette = spec.Decor.ColorPalette,
            ModuleInstances = BuildModuleInstances(spec)
        };
    }

    private static List<RuntimeModuleInstance> BuildModuleInstances(AssetSpec spec)
    {
        var instances = new List<RuntimeModuleInstance>();
        var moduleOrdinal = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);

        foreach (var module in spec.Modules)
        {
            for (var index = 0; index < module.Count; index++)
            {
                moduleOrdinal.TryGetValue(module.ModuleId, out var ordinal);
                moduleOrdinal[module.ModuleId] = ordinal + 1;

                instances.Add(new RuntimeModuleInstance
                {
                    InstanceId = $"{module.ModuleId}#{ordinal + 1}",
                    ModuleId = module.ModuleId,
                    Position = ComputePosition(module.ModuleId, ordinal, module.Count, spec.Footprint),
                    RotationDegrees = ComputeRotation(module.ModuleId),
                    Parameters = BuildParameters(spec, module.ModuleId)
                });
            }
        }

        return instances;
    }

    private static RuntimePosition ComputePosition(string moduleId, int ordinal, int totalCount, FootprintSpec footprint)
    {
        var centeredIndex = ordinal - ((totalCount - 1) / 2.0);

        if (ContainsIgnoreCase(moduleId, ".platform."))
        {
            return new RuntimePosition { X = centeredIndex * 12, Y = 0, Z = 0 };
        }

        if (ContainsIgnoreCase(moduleId, ".concourse."))
        {
            return new RuntimePosition { X = 0, Y = 0, Z = -footprint.Length * 0.18 };
        }

        if (ContainsIgnoreCase(moduleId, ".entrance."))
        {
            return new RuntimePosition { X = centeredIndex * 10, Y = 0, Z = -footprint.Length * 0.42 };
        }

        return new RuntimePosition { X = centeredIndex * 8, Y = 0, Z = footprint.Length * 0.25 };
    }

    private static int ComputeRotation(string moduleId)
    {
        if (ContainsIgnoreCase(moduleId, ".entrance."))
        {
            return 180;
        }

        return 0;
    }

    private static Dictionary<string, string> BuildParameters(AssetSpec spec, string moduleId)
    {
        var parameters = new Dictionary<string, string>
        {
            ["theme"] = spec.Style.Theme,
            ["regional_inspiration"] = spec.Style.RegionalInspiration,
            ["height_class"] = string.IsNullOrWhiteSpace(spec.Footprint.HeightClass) ? "lowrise" : spec.Footprint.HeightClass
        };

        if (ContainsIgnoreCase(moduleId, ".signage."))
        {
            parameters["sign_language"] = string.Join(",", spec.Decor.SignLanguage.DefaultIfEmpty("en"));
        }

        if (spec.Decor.ColorPalette.Count > 0)
        {
            parameters["primary_color"] = spec.Decor.ColorPalette[0];
        }

        return parameters;
    }

    private static string ToStableAssetName(string title)
    {
        var chars = title
            .Trim()
            .ToLowerInvariant()
            .Select(character => char.IsLetterOrDigit(character) ? character : '-')
            .ToArray();

        var slug = new string(chars);
        while (slug.Contains("--"))
        {
            slug = slug.Replace("--", "-");
        }

        return string.IsNullOrWhiteSpace(slug) ? "untitled-station" : slug.Trim('-');
    }

    private static bool ContainsIgnoreCase(string value, string match)
    {
        return value.IndexOf(match, StringComparison.OrdinalIgnoreCase) >= 0;
    }
}
