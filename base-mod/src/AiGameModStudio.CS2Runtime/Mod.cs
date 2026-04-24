#if CITIES_SKYLINES_2
using Colossal.Logging;
using Game;
using Game.Modding;

namespace AiGameModStudio.CS2Runtime
{
    public sealed class Mod : IMod
    {
        public static ILog Log { get; private set; } =
            LogManager.GetLogger("AiGameModStudio.BaseMod").SetShowsErrorsInUI(false);

        public void OnLoad(UpdateSystem updateSystem)
        {
            Log.Info("AI Game Mod Studio Base Mod loading.");

            // Register the runtime system after moving this file into an official CS2 code-mod template.
            updateSystem.UpdateAt<AssetSpecRuntimeSystem>(SystemUpdatePhase.GameSimulation);
        }

        public void OnDispose()
        {
            Log.Info("AI Game Mod Studio Base Mod disposed.");
        }
    }
}
#endif
