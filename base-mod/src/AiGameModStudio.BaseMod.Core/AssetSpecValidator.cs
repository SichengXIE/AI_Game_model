using System.Text.RegularExpressions;

namespace AiGameModStudio.BaseMod.Core;

public sealed class AssetSpecValidator
{
    private static readonly HashSet<string> SupportedGames = new(StringComparer.OrdinalIgnoreCase)
    {
        "cities_skylines_2"
    };

    private static readonly HashSet<string> SupportedAssetTypes = new(StringComparer.OrdinalIgnoreCase)
    {
        "train_station"
    };

    private static readonly HashSet<string> SupportedModules = new(StringComparer.OrdinalIgnoreCase)
    {
        "station.platform.island.small",
        "station.platform.island.medium",
        "station.platform.side.small",
        "station.concourse.basic",
        "station.concourse.glass_hall",
        "station.entrance.single",
        "station.entrance.corner",
        "station.decor.canopy",
        "station.decor.signage"
    };

    public ValidationReport Validate(AssetSpec spec)
    {
        var report = new ValidationReport();

        ValidateIdentity(spec, report);
        ValidateFootprint(spec, report);
        ValidateModules(spec, report);
        ValidateConnections(spec, report);
        ValidateDecor(spec, report);
        ValidateRuntimeConstraints(spec, report);

        return report;
    }

    private static void ValidateIdentity(AssetSpec spec, ValidationReport report)
    {
        if (string.IsNullOrWhiteSpace(spec.SpecVersion))
        {
            report.Error("missing_spec_version", "spec_version is required.", "$.spec_version");
        }

        if (!SupportedGames.Contains(spec.Game))
        {
            report.Error("unsupported_game", $"Unsupported game '{spec.Game}'.", "$.game");
        }

        if (!SupportedAssetTypes.Contains(spec.AssetType))
        {
            report.Error("unsupported_asset_type", $"Unsupported asset_type '{spec.AssetType}'. MVP only supports train_station.", "$.asset_type");
        }

        if (string.IsNullOrWhiteSpace(spec.Title))
        {
            report.Error("missing_title", "title is required.", "$.title");
        }
        else if (spec.Title.Length > 80)
        {
            report.Warning("long_title", "title is longer than 80 characters and may be truncated in-game.", "$.title");
        }
    }

    private static void ValidateFootprint(AssetSpec spec, ValidationReport report)
    {
        if (spec.Footprint.Width <= 0)
        {
            report.Error("invalid_width", "footprint.width must be positive.", "$.footprint.width");
        }

        if (spec.Footprint.Length <= 0)
        {
            report.Error("invalid_length", "footprint.length must be positive.", "$.footprint.length");
        }

        if (spec.Footprint.Width > 256 || spec.Footprint.Length > 512)
        {
            report.Warning("large_footprint", "This footprint is large for the MVP station template and may not fit the current layout generator.", "$.footprint");
        }

        if (string.IsNullOrWhiteSpace(spec.Footprint.HeightClass))
        {
            report.Warning("missing_height_class", "height_class is missing; runtime will default to lowrise.", "$.footprint.height_class");
        }
    }

    private static void ValidateModules(AssetSpec spec, ValidationReport report)
    {
        if (spec.Modules.Count == 0)
        {
            report.Error("missing_modules", "At least one module is required.", "$.modules");
            return;
        }

        for (var index = 0; index < spec.Modules.Count; index++)
        {
            var module = spec.Modules[index];
            var path = $"$.modules[{index}]";

            if (string.IsNullOrWhiteSpace(module.ModuleId))
            {
                report.Error("missing_module_id", "module_id is required.", $"{path}.module_id");
                continue;
            }

            if (!SupportedModules.Contains(module.ModuleId))
            {
                report.Error("unsupported_module", $"Unsupported module_id '{module.ModuleId}'.", $"{path}.module_id");
            }

            if (module.Count <= 0)
            {
                report.Error("invalid_module_count", "module count must be positive.", $"{path}.count");
            }
            else if (module.Count > 12)
            {
                report.Warning("high_module_count", "module count is high for the MVP layout generator.", $"{path}.count");
            }
        }

        if (!spec.Modules.Any(module => ContainsIgnoreCase(module.ModuleId, ".platform.")))
        {
            report.Error("missing_platform", "A train station requires at least one platform module.", "$.modules");
        }

        if (!spec.Modules.Any(module => ContainsIgnoreCase(module.ModuleId, ".entrance.")))
        {
            report.Error("missing_entrance", "A placeable station requires at least one entrance module.", "$.modules");
        }
    }

    private static void ValidateConnections(AssetSpec spec, ValidationReport report)
    {
        if (spec.Connections.RailTracks <= 0)
        {
            report.Error("missing_rail_tracks", "connections.rail_tracks must be positive.", "$.connections.rail_tracks");
        }

        if (spec.Connections.RoadAccess < 0)
        {
            report.Error("invalid_road_access", "connections.road_access cannot be negative.", "$.connections.road_access");
        }

        if (spec.Connections.PedestrianEntries <= 0)
        {
            report.Error("missing_pedestrian_entries", "connections.pedestrian_entries must be positive.", "$.connections.pedestrian_entries");
        }

        var trackCapacity = spec.Modules
            .Where(module => ContainsIgnoreCase(module.ModuleId, ".platform."))
            .Sum(module => ContainsIgnoreCase(module.ModuleId, ".island.") ? module.Count * 2 : module.Count);

        if (trackCapacity > 0 && spec.Connections.RailTracks > trackCapacity)
        {
            report.Warning("rail_track_over_capacity", $"Requested {spec.Connections.RailTracks} rail tracks, but current platform modules imply capacity {trackCapacity}.", "$.connections.rail_tracks");
        }
    }

    private static void ValidateDecor(AssetSpec spec, ValidationReport report)
    {
        for (var index = 0; index < spec.Decor.ColorPalette.Count; index++)
        {
            var color = spec.Decor.ColorPalette[index];
            if (!Regex.IsMatch(color, "^#[0-9a-fA-F]{6}$"))
            {
                report.Error("invalid_color", $"Color '{color}' must use #RRGGBB format.", $"$.decor.color_palette[{index}]");
            }
        }

        if (spec.Decor.SignLanguage.Count == 0)
        {
            report.Warning("missing_sign_language", "No sign languages configured; runtime will default to English.", "$.decor.sign_language");
        }
    }

    private static void ValidateRuntimeConstraints(AssetSpec spec, ValidationReport report)
    {
        if (!spec.RuntimeConstraints.TemplateOnly)
        {
            report.Error("template_only_required", "MVP runtime only supports template_only assets.", "$.runtime_constraints.template_only");
        }

        if (!spec.RuntimeConstraints.RequiresBaseMod)
        {
            report.Error("base_mod_required", "requires_base_mod must be true for this runtime.", "$.runtime_constraints.requires_base_mod");
        }
    }

    private static bool ContainsIgnoreCase(string value, string match)
    {
        return value.IndexOf(match, StringComparison.OrdinalIgnoreCase) >= 0;
    }
}
