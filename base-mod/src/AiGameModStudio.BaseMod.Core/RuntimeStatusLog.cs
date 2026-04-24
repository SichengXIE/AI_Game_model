using System.Text.Json;
using System.Text.Json.Serialization;

namespace AiGameModStudio.BaseMod.Core;

public enum RuntimeStatusLevel
{
    Info,
    Warning,
    Error
}

public sealed record RuntimeStatusEntry(
    [property: JsonPropertyName("timestamp_utc")] DateTimeOffset TimestampUtc,
    [property: JsonPropertyName("level")] RuntimeStatusLevel Level,
    [property: JsonPropertyName("code")] string Code,
    [property: JsonPropertyName("message")] string Message,
    [property: JsonPropertyName("asset_title")] string? AssetTitle = null);

public interface IRuntimeStatusSink
{
    void Write(RuntimeStatusEntry entry);

    void WriteSnapshot(ActiveAssetRuntimeSnapshot snapshot);
}

public sealed class NullRuntimeStatusSink : IRuntimeStatusSink
{
    public static NullRuntimeStatusSink Instance { get; } = new();

    private NullRuntimeStatusSink()
    {
    }

    public void Write(RuntimeStatusEntry entry)
    {
    }

    public void WriteSnapshot(ActiveAssetRuntimeSnapshot snapshot)
    {
    }
}

public sealed class FileRuntimeStatusSink : IRuntimeStatusSink
{
    private static readonly JsonSerializerOptions LogJsonOptions = new(JsonOptions.Default)
    {
        WriteIndented = false
    };

    private readonly ActiveAssetSourceOptions _options;
    private readonly object _lock = new();

    public FileRuntimeStatusSink(ActiveAssetSourceOptions options)
    {
        _options = options;
    }

    public void Write(RuntimeStatusEntry entry)
    {
        _options.EnsureDataDirectory();
        var line = JsonSerializer.Serialize(entry, LogJsonOptions);

        lock (_lock)
        {
            File.AppendAllText(_options.StatusLogPath, line + Environment.NewLine);
        }
    }

    public void WriteSnapshot(ActiveAssetRuntimeSnapshot snapshot)
    {
        _options.EnsureDataDirectory();
        var payload = JsonSerializer.Serialize(snapshot, JsonOptions.Default);

        lock (_lock)
        {
            File.WriteAllText(_options.StatusSnapshotPath, payload);
        }
    }
}
