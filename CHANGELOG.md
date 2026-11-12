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
