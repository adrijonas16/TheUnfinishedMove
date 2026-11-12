# The Unfinished Move — Command Center

**Window:** Thursday 00:00 Peru → Saturday 20:59 Peru  
**Engine:** Unreal Engine 5.8 / Third Person / Blueprint / Windows  
**Goal:** a stable 12–16 minute narrative action-platformer, 65–70% player control and 30–35% cinematic framing.

This is a pre-jam operating plan, not game content. Use the build prompts only after the jam starts.

**Mandatory read order for every AI task:** `CLAUDE.md` → `design/PLAYABILITY_CANON.md` → this file → `design/JAM_PROMPT_PACK.md`. The Playability Canon wins if a previous plan conflicts.

## 1. The game everyone must preserve

**Pitch:** In an abandoned textile factory, a quiet protagonist follows a familiar Visitor through playable “Director’s Cut” worlds. Each recovered cut gives her a physical way to alter the factory route and help the Visitor escape an unfinished chess game.

**Loop:** `Explore factory → Reframe anchor → play 60–90 second cut → gain/alter route → return to factory.`

| Section | Player action | Factory payoff |
|---|---|---|
| Factory I | Follow Visitor; distract one patrol light | Finds Dragon anchor |
| Dragon | Guided flight: steer, evade, Boost | Unlocks high route / Cut Boost |
| Factory II | Boost to higher catwalk | Reaches War anchor |
| War | Stealth/dodge; cut marked rope | Retrieves silver seal |
| Factory III | Insert seal; move crane/fabric bridge | Reaches Cliff anchor |
| Cliff | Frame aura to reveal platforms; time Boost | Unlocks Focus Cut |
| Factory IV | Freeze tagged gate/loom/patrol for 12 seconds | Reaches chess table |
| Chess | Pick preset move; play an escape variant | Farewell and morning ending |

Never add combat, health bars, enemy killing, inventory, full chess, dialogue choices, free dragon flight, Behavior Trees, procedural worlds, open-world travel or menus explaining the plot. Factory stays cold blue-gray/industrial white, with few high narrow windows. The protagonist stays short-haired, hoodie + earbuds, without backpack/large headphones.

**Fun gate:** no empty walk longer than 15–20 seconds. Reframe must edit a visible route inside the factory as well as open cuts. Dragon is three-lane guided traversal; War offers three readable non-combat routes; Cliff teaches temporary camera-revealed platforms; chess branches use one shared escape arena with a distinct learned verb.

## 2. Who does what — a relay, not an agent swarm

Do not launch 49 agents. Only one implementation agent edits a feature at a time.

| Owner | Owns | Never ask it to do |
|---|---|---|
| **You in Unreal** | Maps, visual assembly, pressing Play, screenshots and final choices. | Invent technical architecture alone. |
| **ChatGPT** | Next exact steps from screenshots/errors, prompts, narrative/visual consistency. | Click inside your local Unreal Editor. |
| **Cursor** | Folder/ledger/docs, short bounded code if unavoidable, log reading. | “Make the whole game,” bulk Unreal edits, or simultaneous systems. |
| **Claude API** | Blueprint plan/debug for one named system at a time. | Concept rewrites, agent swarms, repeated art prompts. |
| **Claude Friday 11:00** | Remaining systems, troubleshooting and release checks. | Reopen scope after the loop works. |

### The only Game Studio roles to use

1. `unreal-specialist` — setup and UE constraints.
2. `level-designer` — compact graybox routes.
3. `ue-blueprint-specialist` — one Blueprint at a time.
4. `technical-artist` — materials, lights, simple VFX and Sequencer after the loop works.
5. `qa-tester` / `release-manager` — critical-path tests, packaging and video.

Everything else is intentionally inactive: no combat, economy, networking, analytics, live-ops or large narrative team is required.

### Game Studio skills worth using

| When | Command | Purpose |
|---|---|---|
| First minutes after start | `/setup-engine unreal 5.8` | Configure template for UE rather than Web. |
| After first map | `/map-systems` | Verify Reframe, Boost, Focus Cut and chess boundaries. |
| Before buying/generating model | `/asset-spec` | Check whether it deserves credits. |
| Friday | `/scope-check` | Cut threats to the build. |
| Before each handoff | `/smoke-check` | Test actual critical path. |
| Saturday | `/asset-audit`, `/release-checklist` | Asset declaration, package and video checks. |

Do not run `/prototype`, `/start`, `/team-level` or long documentation pipelines during the jam: the concept already exists.

## 3. Credits and tools

### Claude $25 bridge until Friday 11:00

| Pass | Cap guide | Bounded task | Stop condition |
|---|---:|---|---|
| 1 | US$4 | UE setup / folders / ledger checklist | Project opens, maps named. |
| 2 | US$6 | AlignAnchor + travel + Boost | Dragon round-trip works. |
| 3 | US$5 | PatrolLight + FocusCut | Factory pause works. |
| 4 | US$5 | ChessFinal + active exits | One complete ending works. |
| 5 | US$3 | Fix a real log/error blocker | Packaged test launches. |
| Reserve | US$2 | One unforeseen issue | Never spend vaguely. |

They are caps, not exact model pricing. Do not paste API keys into chat, Git, Cursor rules or a screenshot.

### Asset pools

Use only legitimately owned accounts in compliance with tool/jam terms; never use multiple accounts to bypass quotas.

| Pool | Use | Locked until |
|---|---|---|
| Meshy A (~1100) | Knight, seal, optional crane panel; dragon only if Rodin fails. | Each asset has a graybox location. |
| Meshy B (~1100) | One replacement/revision of a broken hero asset. | End-to-end graybox works. |
| Meshy C (~500) | Emergency. | Saturday. |
| Rodin | One original storm dragon. | Dragon cube route is fun. |
| PBRgen | Wet steel, cloth, mud/grass, basalt only. | Corresponding map exists. |

Use MetaHuman for people; Fab/Quixel and primitives for generic machines, rocks and castle silhouettes. Log every final sourced/generative item in `assets/ASSET_LEDGER.md` and `PRE_JAM_DECLARATION.md`.

## 4. First 35 hours

### Thursday 00:00–01:00 — start and shell

1. Create **new** UE5.8 project: `TheUnfinishedMove`.
2. Select **Games → Third Person → Blueprint → Desktop/Console → Maximum Quality → Starter Content → Windows**.
3. First Git commit: `jam-start`.
4. Create maps: `M_RealRoom`, `M_FactoryHub`, `M_Cut_Dragon`, `M_Cut_WarField`, `M_Cut_Cliff`.
5. Create folders using Cursor prompt A below.
6. Press Play in default map once. Do not continue until it works.

### Thursday 01:00–04:00 — factory graybox only

Build Entry → Loom Patrol Lane → raised Crane Bridge → Focus Gate → Chess Nave in one map. Cubes, ramps, planes/fabric and a primitive chess table are correct. Place checkpoints. The player must be able to run from entrance to chess table with no art, Visitor or dialogue.

**Gate:** a player reaches the chess table in under 3 minutes.

### Thursday morning — ugly, complete pocket maps

| Map | Minimum | Gate |
|---|---|---|
| Dragon | route/spline, 3 obstacles, boost/current rings, landing | 60–90s controllable traversal and return. |
| War | grass plane, low walls, 3 routes, shrine/rope, moving silhouettes | Player gets seal without combat. |
| Cliff | cliffs, four revealed platforms, aura alignment | Player frames and Boosts to end. |

**Gate:** every map returns the player to a factory checkpoint. A black fade is fine at first.

### Thursday afternoon/evening — art only after function

1. Create both MetaHumans: protagonist with short crop/hoodie/earbuds; Visitor same height, charcoal coat, muted amber scarf detail.
2. Generate/import the knight and seal. Generate dragon only once its path is fun.
3. Use Fab/Quixel/primitives for surroundings.
4. Generate materials only for maps already built.
5. Add only: 2-second cut reactions, 12-second hospital chess echo, 8-second farewell. Hide rough body motion with camera cuts.

### Friday 00:00–11:00 — make a precise blocker list

Create `BLOCKERS.md` with: named Blueprint, intended behavior, reproduction, screenshot/log, actual result, priority. At Friday 11:00 fix in this priority:

1. Factory → Dragon → Factory loop.
2. Reframe + Boost.
3. War → seal → crane bridge.
4. Cliff → Focus Cut.
5. Chess choice → one exit.
6. Remaining exits.
7. Art/sound polish.

If time stops at any number, cut the later feature instead of breaking the complete loop.

## 5. Copy/paste prompt library

Before a request, paste the **Universal Context** from `design/JAM_PROMPT_PACK.md`. Give a task to one tool only.

### A. Cursor — immediately after UE project creation

```text
Read CLAUDE.md, project.yaml, PRE_JAM_DECLARATION.md, design/JAM_COMMAND_CENTER.md and design/JAM_PROMPT_PACK.md. This is an Unreal 5.8 Blueprint Windows game called TheUnfinishedMove.

Do not create a game project, maps, assets, Blueprints or C++ gameplay code. Do not modify Unreal .uasset files.

Do only these text/file tasks:
1. Create assets/ASSET_LEDGER.md with these columns: Asset ID, purpose, source/tool, license or terms, created during jam, Meshy pool, credits predicted, credits spent, imported, used in final build, notes.
2. Create BLOCKERS.md with headings: Current build, Reproduction steps, Screenshot/log path, Expected result, Actual result, Owner, Priority, Resolved.
3. Add a short README section “Jam critical path” linking to the Command Center and Prompt Pack.

Show files you will change before editing. Afterwards give the five manual Unreal actions to create the five maps. No unrelated work.
```

### B. Claude / Unreal-specialist — setup audit

```text
You are the Unreal-specialist for a four-day UE5.8 Blueprint jam game. Read design/JAM_COMMAND_CENTER.md and design/JAM_PROMPT_PACK.md. Do not alter narrative, add plugins, write C++ or create open-world architecture.

Audit this setup: Third Person Blueprint, five pocket maps, teleports/fades not world partition, two MetaHumans, Blueprint interaction, brief Sequencer reactions, Windows package.

Return exactly: (1) seven project settings/plugins to enable or avoid; (2) minimal naming/folder convention; (3) risk list with solution plus “cut first”; (4) a manual Editor checklist under 20 steps. Do not edit files.
```

### C. Claude / level-designer — factory build sheet

```text
Act as level-designer. Use only design/JAM_COMMAND_CENTER.md and design/JAM_PROMPT_PACK.md. Design M_FactoryHub as a compact linear graybox for four returns: Entry, Loom Patrol Lane, raised Crane Bridge, Focus Gate and Chess Nave.

For each zone give dimensions in Unreal centimeters, 3–6 primitive actor types, checkpoint location, camera sightline, one mechanic and next visible goal. Fit it in one map with few high/narrow windows; no combat or complex AI.

Then give a 15-item manual actor-placement checklist. Do not create assets or code.
```

### D. Claude API — Reframe / travel / Boost

```text
[Paste Universal Context]

You are the ue-blueprint-specialist. Build the smallest vertical slice: player uses BP_AlignAnchor in M_FactoryHub, travels to Dragon, plays its route, returns to saved Factory transform, then uses a short safe Boost.

Return only: actor/component ownership; variables with UE types/defaults; Blueprint node flow for interact/save transform/map open/return/boost; text state diagram; three editor tests and three recovery cases. No Behavior Tree, C++, world partition or UI menu. Do not generate files.
```

### E. Claude API — Patrol + Focus Cut

```text
[Paste Universal Context]

You are the ue-blueprint-specialist. Design only BP_PatrolLight and BP_FocusCut.

PatrolLight: fixed waypoint movement, cone detection, one fixed distraction target, never game-over; detection briefly closes a route or returns player to nearby cover.
FocusCut: one-use 12-second pause for actors tagged FocusPause; player stays free; loom, gate and patrol restore safely.

Return variables, event flow, tags/interfaces, edge cases and exactly five manual tests. Do not change other systems.
```

### F. Claude API — chess finale

```text
[Paste Universal Context]

You are the ue-blueprint-specialist. Implement BP_ChessFinal as three preset choices, not chess AI: BlockExit, OpenDiagonal and ExposePiece. Each begins a 15–25 second playable escape variation, then converges at one farewell sequence.

Give smallest actor layout, state variables, input/camera lock flow, one active mechanic per route, safe convergence event and test matrix. No dialogue tree, inventory or replayable selection.
```

### G. Any real error

```text
You are a UE5.8 Blueprint debugging partner. Do not redesign the project. Intended behavior: [ONE SENTENCE].

Exact error/log or screenshot description:
[PASTE]

Give one diagnosis ranked by likelihood, then only the next 5–8 exact Unreal Editor actions. Say what screenshot/log to send if they fail. Do not add plugins, C++ or new systems.
```

### H. ChatGPT checkpoint

```text
We are building The Unfinished Move. Screenshot/video and Play behavior: [describe]. Compare it only against the critical path in JAM_COMMAND_CENTER.md. Tell me: (1) passes current gate? (2) next single task; (3) exact UE clicks/Blueprint nodes; (4) one screenshot to send. Do not expand scope.
```

## 6. Rules that keep the submission valid

- Final gameplay, maps, AI assets, art, audio, animations and cinematics must be made after the jam begins. Pre-jam prompts/images are reference only unless properly declared/permitted.
- Final in-game text, voice, video and entry information are English.
- Package Windows build; do not submit only the UE project.
- Record actual 30–60 second 1920×1080+ gameplay.
- Declare every external/Fab/Quixel/AI final asset, licence/terms and tools used.
- Keep content teen-audience-safe.
- Director’s Cut must be visible in play: Reframe → playable cut → altered factory route.

### 45-second proof video

1. 0–6s: factory Reframe alignment.
2. 6–15s: dragon steering/Boost.
3. 15–25s: battlefield dodge and silver seal.
4. 25–34s: cliff platforms appear; Focus Cut freezes route.
5. 34–43s: chess move activates escape.
6. 43–45s: Visitor leaves / white knight close-up.

## 7. Friday 11:00 success definition

By then the game does **not** need polished art. It needs a player who can launch, reach chess, enter/return from all three ugly cuts, use Dragon Boost/War non-combat route/Cliff framing route, and see each cut change one factory obstacle. That transforms later AI tokens into polish rather than rescue.
