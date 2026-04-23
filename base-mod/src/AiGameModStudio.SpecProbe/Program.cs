using System.Text.Json;
using AiGameModStudio.BaseMod.Core;

if (args.Length != 1)
{
    Console.Error.WriteLine("Usage: dotnet run --project base-mod/src/AiGameModStudio.SpecProbe -- <asset-spec.json>");
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
