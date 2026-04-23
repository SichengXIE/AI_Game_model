using System.Text.Json.Serialization;

namespace AiGameModStudio.BaseMod.Core;

public sealed class StationRuntimePlan
{
    [JsonPropertyName("asset_name")]
    public string AssetName { get; init; } = "";

    [JsonPropertyName("display_name")]
    public string DisplayName { get; init; } = "";

    [JsonPropertyName("footprint")]
    public FootprintSpec Footprint { get; init; } = new();

    [JsonPropertyName("connections")]
    public ConnectionSpec Connections { get; init; } = new();

    [JsonPropertyName("style")]
    public StyleSpec Style { get; init; } = new();

    [JsonPropertyName("color_palette")]
    public List<string> ColorPalette { get; init; } = [];

    [JsonPropertyName("module_instances")]
    public List<RuntimeModuleInstance> ModuleInstances { get; init; } = [];
}

public sealed class RuntimeModuleInstance
{
    [JsonPropertyName("instance_id")]
    public string InstanceId { get; init; } = "";

    [JsonPropertyName("module_id")]
    public string ModuleId { get; init; } = "";

    [JsonPropertyName("position")]
    public RuntimePosition Position { get; init; } = new();

    [JsonPropertyName("rotation_degrees")]
    public int RotationDegrees { get; init; }

    [JsonPropertyName("parameters")]
    public Dictionary<string, string> Parameters { get; init; } = new();
}

public sealed class RuntimePosition
{
    [JsonPropertyName("x")]
    public double X { get; init; }

    [JsonPropertyName("y")]
    public double Y { get; init; }

    [JsonPropertyName("z")]
    public double Z { get; init; }
}
