namespace AiGameModStudio.BaseMod.Core;

public sealed class ActiveAssetSourceOptions
{
    public const string DefaultActiveAssetFileName = "active-asset.json";
    public const string DefaultStatusLogFileName = "runtime-status.log";
    public const string DefaultStatusSnapshotFileName = "runtime-status.json";

    public string DataDirectory { get; init; } = GetDefaultDataDirectory();

    public string ActiveAssetFileName { get; init; } = DefaultActiveAssetFileName;

    public string StatusLogFileName { get; init; } = DefaultStatusLogFileName;

    public string StatusSnapshotFileName { get; init; } = DefaultStatusSnapshotFileName;

    public TimeSpan ReloadDebounce { get; init; } = TimeSpan.FromMilliseconds(250);

    public string ActiveAssetPath => Path.Combine(DataDirectory, ActiveAssetFileName);

    public string StatusLogPath => Path.Combine(DataDirectory, StatusLogFileName);

    public string StatusSnapshotPath => Path.Combine(DataDirectory, StatusSnapshotFileName);

    public void EnsureDataDirectory()
    {
        Directory.CreateDirectory(DataDirectory);
    }

    public static string GetDefaultDataDirectory()
    {
        var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        if (string.IsNullOrWhiteSpace(localAppData))
        {
            localAppData = AppContext.BaseDirectory;
        }

        return Path.Combine(
            localAppData,
            "Colossal Order",
            "Cities Skylines II",
            "ModsData",
            "AiGameModStudio");
    }
}
