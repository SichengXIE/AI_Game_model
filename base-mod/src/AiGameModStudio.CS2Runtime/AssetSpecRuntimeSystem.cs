#if CITIES_SKYLINES_2
using System;
using AiGameModStudio.BaseMod.Core;
using Game;
using Game.Prefabs;

namespace AiGameModStudio.CS2Runtime
{
    public partial class AssetSpecRuntimeSystem : GameSystemBase
    {
        private static readonly TimeSpan PollInterval = TimeSpan.FromSeconds(5);
        private ActiveAssetHotReloadWatcher? _hotReloadWatcher;
        private ActiveAssetRuntimeService? _runtimeService;
        private Cs2StationPrefabBinder? _prefabBinder;
        private DateTime _lastPollAtUtc = DateTime.MinValue;

        protected override void OnCreate()
        {
            base.OnCreate();
            var options = new ActiveAssetSourceOptions();
            var fileSink = new FileRuntimeStatusSink(options);
            var statusSink = new GameRuntimeStatusSink(fileSink);
            _runtimeService = new ActiveAssetRuntimeService(options, statusSink);
            _prefabBinder = new Cs2StationPrefabBinder(
                World.GetOrCreateSystemManaged<PrefabSystem>(),
                EntityManager);
            _hotReloadWatcher = new ActiveAssetHotReloadWatcher(_runtimeService);
            _hotReloadWatcher.Reloaded += snapshot =>
            {
                if (snapshot.State != ActiveAssetRuntimeState.Unchanged)
                {
                    Mod.Log.Info($"Asset Spec hot reload finished with state {snapshot.State}.");
                }

                if (snapshot.RuntimePlan is not null)
                {
                    _prefabBinder?.PrepareBinding(snapshot.RuntimePlan);
                }
            };

            Mod.Log.Info($"Asset Spec runtime system created. Data directory: {options.DataDirectory}");
            var initialSnapshot = _hotReloadWatcher.Start(loadImmediately: true);
            if (initialSnapshot.RuntimePlan is not null)
            {
                _prefabBinder.PrepareBinding(initialSnapshot.RuntimePlan);
            }
        }

        protected override void OnUpdate()
        {
            if (_hotReloadWatcher is null || (DateTime.UtcNow - _lastPollAtUtc) < PollInterval)
            {
                return;
            }

            _lastPollAtUtc = DateTime.UtcNow;
            _hotReloadWatcher.Poll();
        }

        protected override void OnDestroy()
        {
            _hotReloadWatcher?.Dispose();
            Mod.Log.Info("Asset Spec runtime system destroyed.");
            base.OnDestroy();
        }

        private sealed class GameRuntimeStatusSink : IRuntimeStatusSink
        {
            private readonly IRuntimeStatusSink _innerSink;

            public GameRuntimeStatusSink(IRuntimeStatusSink innerSink)
            {
                _innerSink = innerSink;
            }

            public void Write(RuntimeStatusEntry entry)
            {
                _innerSink.Write(entry);

                var message = $"{entry.Code}: {entry.Message}";
                if (entry.Level == RuntimeStatusLevel.Error)
                {
                    Mod.Log.Error(message);
                }
                else
                {
                    Mod.Log.Info(message);
                }
            }

            public void WriteSnapshot(ActiveAssetRuntimeSnapshot snapshot)
            {
                _innerSink.WriteSnapshot(snapshot);
            }
        }
    }
}
#endif
