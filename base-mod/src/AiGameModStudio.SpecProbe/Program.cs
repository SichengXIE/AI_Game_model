using System.Text.Json;
using AiGameModStudio.BaseMod.Core;

if (args.Length == 1 && args[0] == "--default-data-dir")
{
    Console.WriteLine(ActiveAssetSourceOptions.GetDefaultDataDirectory());
    return 0;
}

if (args.Length == 2 && args[0] == "--data-dir")
{
    var options = new ActiveAssetSourceOptions
    {
        DataDirectory = Path.GetFullPath(args[1])
    };
    var service = new ActiveAssetRuntimeService(options, new FileRuntimeStatusSink(options));
    var snapshot = service.LoadActiveAsset(force: true);
    Console.WriteLine(JsonSerializer.Serialize(snapshot, JsonOptions.Default));

    return snapshot.State switch
    {
        ActiveAssetRuntimeState.Loaded => 0,
        ActiveAssetRuntimeState.Missing => 65,
        ActiveAssetRuntimeState.Invalid => 66,
        ActiveAssetRuntimeState.Failed => 67,
        _ => 68
    };
}

if (args.Length != 1)
{
    Console.Error.WriteLine("Usage:");
    Console.Error.WriteLine("  dotnet run --project base-mod/src/AiGameModStudio.SpecProbe -- <asset-spec.json>");
    Console.Error.WriteLine("  dotnet run --project base-mod/src/AiGameModStudio.SpecProbe -- --data-dir <directory>");
    Console.Error.WriteLine("  dotnet run --project base-mod/src/AiGameModStudio.SpecProbe -- --default-data-dir");
    return 64;
}

var specPath = Path.GetFullPath(args[0]);
AssetSpec spec;

try
{
    spec = AssetSpecLoader.LoadFromFile(specPath);
}
catch (Exception exception)
{
    Console.Error.WriteLine($"Failed to load Asset Spec: {exception.Message}");
    return 65;
}

var validator = new AssetSpecValidator();
var report = validator.Validate(spec);

foreach (var issue in report.Issues)
{
    Console.Error.WriteLine($"{issue.Severity}: {issue.Code} at {issue.Path}: {issue.Message}");
}

if (report.HasErrors)
{
    Console.Error.WriteLine("Asset Spec is invalid.");
    return 66;
}

var plan = new StationTemplateBuilder().Build(spec);
Console.WriteLine(JsonSerializer.Serialize(plan, JsonOptions.Default));
return 0;
