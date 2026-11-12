# Changelog

## 2026-11-12 00:20 (UTC-5) — jam-start
- New UE 5.8 Third Person Blueprint project created at jam start.
- Planning docs (design/), CLAUDE.md, PRE_JAM_DECLARATION.md, asset ledger, blockers list.

## 2026-11-12 00:35 — maps + factory graybox
- Editor bridge Content/Python/init_unreal.py (editor-only, runs scripts dropped in Saved/ClaudeQueue) and helpers Content/Python/tum_lib.py.
- /Game/TUM folder tree; maps M_RealRoom, M_FactoryHub, M_Cut_Dragon, M_Cut_WarField, M_Cut_Cliff (base cold lighting, floor, PlayerStart).
- M_FactoryHub graybox (78 actors): Entry, Loom Patrol Lane, Dragon anchor (lamp + round window), Crane Bridge (DragonLift, raised catwalk, crane), Focus Gate (open for gate test), Chess Nave with 3 exits; checkpoints CP_*; startup/default map = M_FactoryHub.

## 2026-11-12 00:45 — Cut Boost + core classes
- BP_GameProgress (GameInstance: return transform, cut flags, Boost/Focus unlocks), BP_TUMCharacter (child of template) with Cut Boost (IA_Boost: LeftShift / RB; LaunchCharacter 1500 fwd + 480 up, 1.2 s cooldown), BP_TUMGameMode; set as project defaults.
- Crane zone: three crate steps (DragonLift) up to the 300 cm deck; 640 cm Boost gap to the raised catwalk — tested in Play: reachable only with Boost.
- Bridge skips while Play-In-Editor runs.

## Thu — Vertical slice: Match Cut → Dragon → Factory
- BP_AlignAnchor (Verbs): stand on the floor ring near the loom lane, line the round lamp up with the round window and hold ~0.35 s → silver flash, return point saved, fade, open M_Cut_Dragon.
- BP_DragonRoute + M_Cut_Dragon graybox: guided forward flight, 3 lanes, storm walls, 3 wind currents that need a Boost (soft push-back if missed), end → DragonDone + HasBoost, back to the factory.
- BP_FactoryRoute: returns the player to the saved spot, shows the DragonLift crates, removes the used anchor, unlocks Boost from progress.
- BP_TUMCharacter: Boost locked by default; on foot = launch, while flying = 0.7 s speed burst; records LastBoostTime.

## Thu — First packaged Windows build (Test01)
- Packaged via RunUAT BuildCookRun (Development, 5 TUM maps). Fix: GameFeatureData entry in AssetManagerSettings (cook failed without it); UAT needs -unrealexe for this content-only project. Size ~1 GB (to trim later).
