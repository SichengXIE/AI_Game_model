using System.Text.Json;

namespace AiGameModStudio.BaseMod.Core;

public static class AssetSpecLoader
{
    public static AssetSpec LoadFromFile(string path)
    {
        if (!File.Exists(path))
        {
            throw new FileNotFoundException("Asset Spec file was not found.", path);
        }

        using var stream = File.OpenRead(path);
        var spec = JsonSerializer.Deserialize<AssetSpec>(stream, JsonOptions.Default);

        return spec ?? throw new InvalidDataException("Asset Spec file is empty or invalid JSON.");
    }
}
