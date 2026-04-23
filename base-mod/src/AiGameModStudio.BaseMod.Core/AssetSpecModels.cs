using System.Text.Json.Serialization;

namespace AiGameModStudio.BaseMod.Core;

public sealed class AssetSpec
{
    [JsonPropertyName("spec_version")]
    public string SpecVersion { get; init; } = "";

    [JsonPropertyName("game")]
    public string Game { get; init; } = "";

    [JsonPropertyName("asset_type")]
    public string AssetType { get; init; } = "";

    [JsonPropertyName("title")]
    public string Title { get; init; } = "";

    [JsonPropertyName("style")]
    public StyleSpec Style { get; init; } = new();

    [JsonPropertyName("footprint")]
    public FootprintSpec Footprint { get; init; } = new();

    [JsonPropertyName("modules")]
    public List<ModuleSpec> Modules { get; init; } = [];

    [JsonPropertyName("connections")]
    public ConnectionSpec Connections { get; init; } = new();

    [JsonPropertyName("decor")]
    public DecorSpec Decor { get; init; } = new();

    [JsonPropertyName("runtime_constraints")]
    public RuntimeConstraintsSpec RuntimeConstraints { get; init; } = new();
}

public sealed class StyleSpec
{
    [JsonPropertyName("theme")]
    public string Theme { get; init; } = "";

    [JsonPropertyName("regional_inspiration")]
    public string RegionalInspiration { get; init; } = "";

    [JsonPropertyName("materials")]
    public List<string> Materials { get; init; } = [];
}

public sealed class FootprintSpec
{
    [JsonPropertyName("width")]
    public int Width { get; init; }

    [JsonPropertyName("length")]
    public int Length { get; init; }

    [JsonPropertyName("height_class")]
    public string HeightClass { get; init; } = "";
}

public sealed class ModuleSpec
{
    [JsonPropertyName("module_id")]
    public string ModuleId { get; init; } = "";

    [JsonPropertyName("count")]
    public int Count { get; init; }
}

public sealed class ConnectionSpec
{
    [JsonPropertyName("rail_tracks")]
    public int RailTracks { get; init; }

    [JsonPropertyName("road_access")]
    public int RoadAccess { get; init; }

    [JsonPropertyName("pedestrian_entries")]
    public int PedestrianEntries { get; init; }
}

public sealed class DecorSpec
{
    [JsonPropertyName("sign_language")]
    public List<string> SignLanguage { get; init; } = [];

    [JsonPropertyName("color_palette")]
    public List<string> ColorPalette { get; init; } = [];
}

public sealed class RuntimeConstraintsSpec
{
    [JsonPropertyName("template_only")]
    public bool TemplateOnly { get; init; }

    [JsonPropertyName("requires_base_mod")]
    public bool RequiresBaseMod { get; init; }

    [JsonPropertyName("base_mod_min_version")]
    public string BaseModMinVersion { get; init; } = "";
}
