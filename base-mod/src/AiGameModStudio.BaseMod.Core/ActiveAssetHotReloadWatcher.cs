namespace AiGameModStudio.BaseMod.Core;

public sealed class ActiveAssetHotReloadWatcher : IDisposable
{
    private readonly ActiveAssetRuntimeService _runtimeService;
    private readonly object _lock = new();
    private FileSystemWatcher? _watcher;
    private Timer? _debounceTimer;
    private bool _disposed;

    public ActiveAssetHotReloadWatcher(ActiveAssetRuntimeService runtimeService)
    {
        _runtimeService = runtimeService;
    }

    public event Action<ActiveAssetRuntimeSnapshot>? Reloaded;

    public ActiveAssetRuntimeSnapshot Start(bool loadImmediately = true)
    {
        var options = _runtimeService.Options;
        options.EnsureDataDirectory();

        _watcher = new FileSystemWatcher(options.DataDirectory, options.ActiveAssetFileName)
        {
            NotifyFilter = NotifyFilters.FileName
                | NotifyFilters.LastWrite
                | NotifyFilters.Size
                | NotifyFilters.CreationTime
        };
        _watcher.Changed += OnFileChanged;
        _watcher.Created += OnFileChanged;
        _watcher.Deleted += OnFileChanged;
        _watcher.Renamed += OnFileChanged;
        _watcher.EnableRaisingEvents = true;

        return loadImmediately
            ? _runtimeService.LoadActiveAsset(force: true)
            : new ActiveAssetRuntimeSnapshot
            {
                State = ActiveAssetRuntimeState.Unchanged,
                SpecPath = options.ActiveAssetPath,
                Message = "Hot reload watcher started without initial load."
            };
    }

    public ActiveAssetRuntimeSnapshot Poll()
    {
        return _runtimeService.LoadActiveAsset(force: false);
    }

    private void OnFileChanged(object sender, FileSystemEventArgs args)
    {
        lock (_lock)
        {
            _debounceTimer?.Dispose();
            _debounceTimer = new Timer(
                _ => ReloadNow(),
                null,
                _runtimeService.Options.ReloadDebounce,
                Timeout.InfiniteTimeSpan);
        }
    }

    private void ReloadNow()
    {
        if (_disposed)
        {
            return;
        }

        var snapshot = _runtimeService.LoadActiveAsset(force: true);
        Reloaded?.Invoke(snapshot);
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        _watcher?.Dispose();
        _debounceTimer?.Dispose();
    }
}
