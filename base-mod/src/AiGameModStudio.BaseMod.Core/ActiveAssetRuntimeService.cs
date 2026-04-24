namespace AiGameModStudio.BaseMod.Core;

public sealed class ActiveAssetRuntimeService
{
    private readonly ActiveAssetSourceOptions _options;
    private readonly IRuntimeStatusSink _statusSink;
    private FileSignature? _lastLoadedSignature;
    private ActiveAssetRuntimeState? _lastEmittedState;

    public ActiveAssetRuntimeService(
        ActiveAssetSourceOptions? options = null,
        IRuntimeStatusSink? statusSink = null)
    {
        _options = options ?? new ActiveAssetSourceOptions();
        _statusSink = statusSink ?? NullRuntimeStatusSink.Instance;
    }

    public ActiveAssetSourceOptions Options => _options;

    public ActiveAssetRuntimeSnapshot LoadActiveAsset(bool force = false)
    {
        _options.EnsureDataDirectory();

        var specPath = _options.ActiveAssetPath;
        var checkedAtUtc = DateTimeOffset.UtcNow;
        if (!File.Exists(specPath))
        {
            _lastLoadedSignature = null;
            if (!force && _lastEmittedState == ActiveAssetRuntimeState.Missing)
            {
                return new ActiveAssetRuntimeSnapshot
                {
                    State = ActiveAssetRuntimeState.Unchanged,
                    SpecPath = specPath,
                    CheckedAtUtc = checkedAtUtc,
                    Message = "Active Asset Spec is still missing."
                };
            }

            return EmitSnapshot(
                new ActiveAssetRuntimeSnapshot
                {
                    State = ActiveAssetRuntimeState.Missing,
                    SpecPath = specPath,
                    CheckedAtUtc = checkedAtUtc,
                    Message = $"No active Asset Spec found at {specPath}."
                },
                RuntimeStatusLevel.Info,
                "active_spec_missing");
        }

        var signature = FileSignature.FromFile(specPath);
        if (!force && _lastLoadedSignature == signature)
        {
            return new ActiveAssetRuntimeSnapshot
            {
                State = ActiveAssetRuntimeState.Unchanged,
                SpecPath = specPath,
                CheckedAtUtc = checkedAtUtc,
                LastWriteTimeUtc = signature.LastWriteTimeUtc,
                Message = "Active Asset Spec has not changed since the last successful load attempt."
            };
        }

        try
        {
            var spec = AssetSpecLoader.LoadFromFile(specPath);
            var report = new AssetSpecValidator().Validate(spec);
            _lastLoadedSignature = signature;

            foreach (var issue in report.Issues)
            {
                _statusSink.Write(new RuntimeStatusEntry(
                    TimestampUtc: DateTimeOffset.UtcNow,
                    Level: issue.Severity == ValidationSeverity.Error ? RuntimeStatusLevel.Error : RuntimeStatusLevel.Warning,
                    Code: issue.Code,
                    Message: $"{issue.Path}: {issue.Message}",
                    AssetTitle: spec.Title));
            }

            if (report.HasErrors)
            {
                return EmitSnapshot(
                    new ActiveAssetRuntimeSnapshot
                    {
                        State = ActiveAssetRuntimeState.Invalid,
                        SpecPath = specPath,
                        CheckedAtUtc = checkedAtUtc,
                        LastWriteTimeUtc = signature.LastWriteTimeUtc,
                        Message = "Active Asset Spec has validation errors; runtime plan was not built.",
                        AssetTitle = spec.Title,
                        Issues = report.Issues
                    },
                    RuntimeStatusLevel.Error,
                    "active_spec_invalid");
            }

            var plan = new StationTemplateBuilder().Build(spec);
            return EmitSnapshot(
                new ActiveAssetRuntimeSnapshot
                {
                    State = ActiveAssetRuntimeState.Loaded,
                    SpecPath = specPath,
                    CheckedAtUtc = checkedAtUtc,
                    LastWriteTimeUtc = signature.LastWriteTimeUtc,
                    Message = $"Loaded Asset Spec '{plan.DisplayName}' with {plan.ModuleInstances.Count} module instances.",
                    AssetTitle = spec.Title,
                    RuntimePlan = plan,
                    Issues = report.Issues
                },
                RuntimeStatusLevel.Info,
                "active_spec_loaded");
        }
        catch (Exception exception)
        {
            _lastLoadedSignature = signature;
            return EmitSnapshot(
                new ActiveAssetRuntimeSnapshot
                {
                    State = ActiveAssetRuntimeState.Failed,
                    SpecPath = specPath,
                    CheckedAtUtc = checkedAtUtc,
                    LastWriteTimeUtc = signature.LastWriteTimeUtc,
                    Message = $"Failed to load active Asset Spec: {exception.Message}"
                },
                RuntimeStatusLevel.Error,
                "active_spec_load_failed");
        }
    }

    private ActiveAssetRuntimeSnapshot EmitSnapshot(
        ActiveAssetRuntimeSnapshot snapshot,
        RuntimeStatusLevel level,
        string code)
    {
        _statusSink.Write(new RuntimeStatusEntry(
            TimestampUtc: DateTimeOffset.UtcNow,
            Level: level,
            Code: code,
            Message: snapshot.Message,
            AssetTitle: snapshot.AssetTitle));
        _statusSink.WriteSnapshot(snapshot);
        _lastEmittedState = snapshot.State;
        return snapshot;
    }

    private readonly record struct FileSignature(DateTimeOffset LastWriteTimeUtc, long Length)
    {
        public static FileSignature FromFile(string path)
        {
            var info = new FileInfo(path);
            return new FileSignature(info.LastWriteTimeUtc, info.Length);
        }
    }
}
