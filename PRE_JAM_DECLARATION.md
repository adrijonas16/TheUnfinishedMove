# Pre-Jam Declaration — The Unfinished Move (working title earlier: La partida pendiente)

**Jam:** 2026 Epic AI MegaJam  
**Prepared before the build window:** 11 November 2026  
**Purpose:** transparently declare planning material, concept art, prompts and support scripts prepared before development began.

## Scope statement

The items below were created only for planning, visual exploration, documentation and workflow preparation. **No Unreal gameplay, levels, Blueprints, packaged builds, final game assets, final animations or playable game systems were built before the jam start.**

Any pre-jam item that is used in the final submission will be credited here and in the devlog/submission notes.

---

## 1. Planning and narrative documents

| File | Purpose | Intended use during jam |
|---|---|---|
| `design/game-brief.md` | Current short game brief: factory hub, three playable cuts, chess ending and strict scope. | Narrative/production reference. |
| `design/PLAYABLE_TRAILER_SCRIPT.md` | Scene-by-scene playable script, camera guidance, prompts and technical limits. | Narrative/level/cinematic reference. |
| `design/TOMORROW_START_RUNBOOK.md` | Day-by-day build order, Blueprint list, tool allocation and Claude prompts. | Production checklist. |
| `design/JAM_PROMPT_PACK.md` | Unreal, asset, animation, cinematic and quality-gate prompt library. | Prompt/reference only; final generated content happens during jam. |
| `design/JAM_COMMAND_CENTER.md` | Tool allocation, role relay, post-start schedule, implementation prompts and compliance checklist. | Production/reference only; final generated content happens during jam. |
| `../DIRECTORS_CUT_GAME_BIBLE.md` | Earlier concept/narrative exploration. | Background reference only; not necessarily used verbatim. |
| `../PLAN_MAESTRO_LA_PARTIDA_PENDIENTE.md` | Earlier production-plan draft. | Background reference only; superseded by the runbook. |

## 2. Pre-jam concept images

All images below are **concept art/reference material only**. They are not imported game-ready models, textures, animation, gameplay maps or UI assets.

| Local source | Description | Planned use |
|---|---|---|
| `../generated_images/exec-0c5c56a4-99c1-416a-b228-3287970d7445.png` | Factory chess scene with the protagonist’s approved short, dense curly hairstyle. | Character, lighting and composition reference. |
| `../generated_images/exec-31933771-8995-4c24-a8f0-3d363bda1d50.png` | Protagonist concept portrait; short dark curls, dark jacket, white knight. | Character reference. |
| `../generated_images/exec-f0bccb84-b991-4907-86a4-a6a20223ca2f.png` | Visitor concept portrait. | Character reference. |
| `../generated_images/exec-912d75fa-085e-4a66-89da-8afab5c5ef8d.png` | Earlier factory/chess composition study. | Lighting/environment reference only; superseded by the corrected version above. |
| `../generated_images/exec-a668f36b-5f54-4870-a15a-3950995a0acc.png` | Additional early character/environment concept variation. | Exploration/reference only. |

## 3. Prompt families prepared before the jam

These prompts are planning material. Any final asset generated during the jam will be logged separately with its tool, date and purpose.

| Prompt family | Intended tool/use | Summary |
|---|---|---|
| Factory chess concept | Image generation | Rainy abandoned textile factory, wet concrete, blue/amber lighting, chess table, protagonist with short dense curls, visitor with amber accent. |
| Protagonist visual guide | Image generation / character reference | Young adult, short dense dark curly crop, close sides, oversized dark jacket, headphones and worn white knight. |
| Visitor visual guide | Image generation / character reference | Young adult, open posture, structured dark coat and restrained amber detail; warm/direct but not villainous. |
| Dragon prop | Hyper3D Rodin candidate | Original non-copyrighted dragon suitable for a spline/set piece; no combat boss requirement. |
| Chess knight prop | Meshy/Tripo candidate | Worn white ceramic/carved chess knight, emotionally important, game-ready PBR prop. |
| Sealed-object prop | Meshy/Tripo candidate | Small original industrial memory core/object; valuable, personal and non-weapon-like. |
| Factory materials | PBRgen candidate | Wet oxidized metal, damp concrete, industrial fabric and related PBR maps. |
| Character performance | Rokoko/iClone direction | Adult protagonist’s startled entry reaction, chess gestures and restrained final smile. |
| Unreal/Claude implementation | Claude Code + Unreal MCP | Small reusable Blueprints: alignment, cut transition, boost, visitor beats, chess final and escape consequence. |
| Command-center implementation prompts | Cursor, Claude Code and Unreal workflow | Bounded setup, graybox, Blueprint debugging, QA and release prompts. |

## 4. Support scripts and setup materials

| File/tool | Purpose | Game-content status |
|---|---|---|
| `../build_visual_bible.py` | Generated a planning document from the narrative/visual bible. | Documentation support only; not game code. |
| Claude Code Game Studios repository/template | Workflow, documentation and task structure. | Template/setup only; gameplay will be created during jam. |
| Editor automation scripts from an earlier, unrelated personal project (Python helpers that write Blueprint graphs, place actors and import assets in Unreal) | Tooling to drive the Unreal editor from Claude. | Tooling only; any helper reused in this repo is marked with its origin. No gameplay, maps or assets from that project are used. |
| Meshy community CC0 models downloaded before the jam (street furniture, mugs, monitor) | Possible generic props. | Only used if logged in the asset ledger with author and CC0 licence. |

## 5. Items explicitly not prepared before the jam

- Unreal project gameplay implementation.
- Finished maps or factory graybox.
- Blueprints, C++ code, AI logic or cutscene sequences for the submitted game.
- Final game characters, rigs, animations, textures, audio, VFX, UI or playable levels.
- Packaged build or gameplay video.

## 6. During-jam update log

Add every externally sourced or AI-assisted final asset here as it is created or imported.

| Date/time | Tool/source | Asset or change | License/terms checked | Used in build? | Notes |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 7. Submission checklist

- [ ] Keep this declaration in the repository.
- [ ] Add all final Fab assets, generated models, music/SFX and plugins to the update log.
- [ ] List every required license/attribution in the submission notes.
- [ ] List tools used, especially any partner tool required for a partner prize.
- [ ] Link the devlog that shows the game being built during the jam.
