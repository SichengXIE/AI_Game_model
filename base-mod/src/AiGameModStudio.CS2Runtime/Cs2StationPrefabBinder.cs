#if CITIES_SKYLINES_2
#nullable enable
using AiGameModStudio.BaseMod.Core;
using Game.Prefabs;
using Unity.Entities;

namespace AiGameModStudio.CS2Runtime
{
    public sealed class Cs2StationPrefabBinder
    {
        private readonly PrefabSystem _prefabSystem;
        private readonly EntityManager _entityManager;

        public Cs2StationPrefabBinder(PrefabSystem prefabSystem, EntityManager entityManager)
        {
            _prefabSystem = prefabSystem;
            _entityManager = entityManager;
        }

        public void PrepareBinding(StationRuntimePlan plan)
        {
            Mod.Log.Info(
                $"Preparing CS2 prefab binding for '{plan.DisplayName}' with " +
                $"{plan.ModuleInstances.Count} module instances.");

            foreach (var module in plan.ModuleInstances)
            {
                Mod.Log.Info(
                    $"Module binding candidate: {module.InstanceId} -> {module.ModuleId} " +
                    $"at ({module.Position.X:0.##}, {module.Position.Y:0.##}, {module.Position.Z:0.##}).");
            }

            // Next binding step:
            // 1. Resolve template PrefabBase values through PrefabSystem.
            // 2. Duplicate or instantiate supported station/prefab templates.
            // 3. Add/update Game.Objects transform and color/material component data through EntityManager.
            // 4. Attach generated sub-objects and connection anchors after prefab references are stable.
            _ = _prefabSystem;
            _ = _entityManager;
        }
    }
}
#nullable restore
#endif
