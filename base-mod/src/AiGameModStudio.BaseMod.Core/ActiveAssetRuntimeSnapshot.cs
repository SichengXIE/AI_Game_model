using System.Text.Json.Serialization;

namespace AiGameModStudio.BaseMod.Core;

public enum ActiveAssetRuntimeState
{
    Missing,
    Unchanged,
    Loaded,
    Invalid,
    Failed
}

public sealed class ActiveAssetRuntimeSnapshot
{
    [JsonPropertyName("state")]
    public ActiveAssetRuntimeState State { get; init; }

    [JsonPropertyName("spec_path")]
    public string SpecPath { get; init; } = "";

    [JsonPropertyName("checked_at_utc")]
    public DateTimeOffset CheckedAtUtc { get; init; } = DateTimeOffset.UtcNow;

    [JsonPropertyName("last_write_time_utc")]
    public DateTimeOffset? LastWriteTimeUtc { get; init; }

    [JsonPropertyName("message")]
    public string Message { get; init; } = "";

    [JsonPropertyName("asset_title")]
    public string? AssetTitle { get; init; }

    [JsonPropertyName("runtime_plan")]
    public StationRuntimePlan? RuntimePlan { get; init; }

    [JsonPropertyName("issues")]
    public List<ValidationIssue> Issues { get; init; } = [];

    [JsonIgnore]
    public bool IsUsable => State == ActiveAssetRuntimeState.Loaded && RuntimePlan is not null;
}
