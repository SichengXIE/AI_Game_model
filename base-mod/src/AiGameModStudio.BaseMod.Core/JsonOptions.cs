using System.Text.Json;
using System.Text.Json.Serialization;

namespace AiGameModStudio.BaseMod.Core;

public static class JsonOptions
{
    public static readonly JsonSerializerOptions Default = new()
    {
        AllowTrailingCommas = true,
        PropertyNameCaseInsensitive = true,
        ReadCommentHandling = JsonCommentHandling.Skip,
        WriteIndented = true,
        Converters = { new JsonStringEnumConverter() }
    };
}
