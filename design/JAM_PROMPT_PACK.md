# The Unfinished Move Prompt Pack

Use this file only after the Epic AI MegaJam build window starts. It is a planning and prompt library, not final game content.

## 0. Credit rules

1. Do not generate a 3D asset until a graybox proves where it will appear and why it cannot be a simple Unreal/Fab/Quixel object.
2. Generate one candidate at a time. Review it in Unreal before paying for a replacement.
3. Meshy account A is the production pool. Account B stays locked until the first end-to-end playable build exists. Account C is emergency only.
4. Use MetaHuman and Unreal Sequencer for people; preserve Meshy/Rodin credits for the dragon and signature props.
5. The final submission needs English-only visible text, spoken dialogue, subtitles, store description and gameplay video.

## 1. Universal context

Paste this at the top of every Claude or Cursor request.

```text
Project: The Unfinished Move, a 12–16 minute third-person Unreal Engine 5 narrative action-platformer for Windows.

Core premise: In a rain-soaked abandoned textile factory, a quiet protagonist follows a familiar Visitor. The factory is the official version of the story. Dragon flight, an open medieval battlefield and a cliff above clouds are playable Director's Cut scenes she imagined while growing up. Every cut changes a physical route in the factory.

Non-negotiable mechanics:
- Reframe of Continuity: camera alignment reveals a cut or route.
- Cut Lived: 1–3 second reaction shot, safe teleport to a pocket level, return to the factory checkpoint.
- Inherited Boost: one short dash/boost reskinned by scene.
- Focus Cut: a 12-second pause of marked machinery, doors and patrols.
- Chess finale: three preset moves cause three short active escape variants.

Do not build: combat, inventory, full chess, dialogue trees, enemy health, open world, free dragon flight, complex navigation AI, procedural systems or menus that explain the plot.

Art constraints: cold blue-gray and industrial white factory lighting; no yellow ambient light; few narrow high windows; wet textile machinery and hanging fabric. The protagonist has fair skin, a very short dense dark curly crop with close sides/back, a charcoal hooded sweatshirt and tiny black earbuds. No backpack, long hair or large headphones. The Visitor is the same height, fair skinned, with shoulder-length dark brown natural waves, a practical charcoal coat and one small muted amber scarf detail. Never copy a real person's identity.

Return only: changed files, exact setup steps, compile/playtest checklist, and risks. Do not modify unrelated files.
```

## 2. Cursor setup

Install Cursor from its official Windows download page. Open the Unreal project root, not the Engine folder. Connect the project Git repository before asking Cursor to change anything.

### Cursor project rules prompt

```text
Read CLAUDE.md, project.yaml, design/game-brief.md, design/PLAYABLE_TRAILER_SCRIPT.md, design/TOMORROW_START_RUNBOOK.md and design/JAM_PROMPT_PACK.md before editing.

This is a four-day Unreal 5 jam project. Favor Blueprint-compatible, small, testable components. Do not introduce plugins, large frameworks, multiplayer, GAS, behavior trees or new systems unless explicitly asked. Work on only the named files. Before writing code, state a five-line plan. After edits, provide the exact Unreal Editor test steps.
```

### Cursor task prompt: project structure

```text
[Paste Universal context]

Create only the folders and placeholder documentation needed for this Unreal project:
Content/Maps, Content/Blueprints, Content/Art/Characters, Content/Art/Environment/Factory, Content/Art/Environment/Cuts, Content/Art/Props, Content/Audio, Content/Cinematics, Content/UI.

Create assets/ASSET_LEDGER.md with columns: Asset ID, purpose, source/tool, license or terms, created during jam, Meshy pool, credits predicted, credits spent, imported, used in final build, notes.

Do not create gameplay code. Do not move existing files. Return a checklist for manually creating the maps M_RealRoom, M_FactoryHub, M_Cut_Dragon, M_Cut_WarField and M_Cut_Cliff in Unreal.
```

## 3. Core Unreal prompts

Use Claude for one system at a time. Do not give the same task to Cursor and Claude.

### BP AlignAnchor

```text
[Paste Universal context]

Design BP_AlignAnchor for a camera-alignment interaction. It must activate only when the player is inside a small trigger volume, looking toward a target direction within a configurable angle, and presses Interact. The actor needs: CutId, target scene reference, angle tolerance, visual hint mesh, completion event and one-shot state. Use Blueprint-friendly pseudocode and exact variables/nodes. No UI tutorial panel; use a subtle material/VFX cue. Include a test with three wrong angles and one correct angle.
```

### BP CutSequenceManager

```text
[Paste Universal context]

Design BP_CutSequenceManager. It receives a CutId, saves the player's factory return transform and checkpoint, plays a 1–3 second Level Sequence, locks input briefly, opens or teleports to the relevant pocket map, restores control, then returns the player safely after the cut completes. It must not stream a giant world or leave duplicate player pawns. Describe the simplest Unreal 5 Blueprint implementation and a recovery path if a map load fails.
```

### BP CutBoostComponent

```text
[Paste Universal context]

Implement the design for BP_CutBoostComponent: one short directional impulse with configurable strength, duration, cooldown, scene VFX/SFX and collision safety. It is used as industrial boost, dragon air current, war sprint and cliff wind jump. It must not pass through walls, stack infinitely or require a stamina system. Give Blueprint variables, events and a four-case test checklist.
```

### Factory patrols

```text
[Paste Universal context]

Design BP_PatrolLight for a jam scope. A patrol travels between fixed scene markers, sweeps a cone light, can be distracted to one fixed alternate marker and reports detection to the player. Detection must never cause a game over; it either closes a route for a few seconds or returns the player to nearby cover. Avoid Behavior Trees and complex AI perception. Provide a Blueprint state machine with IdleRoute, Distracted, Detecting and Cooldown.
```

### Focus Cut

```text
[Paste Universal context]

Design BP_FocusCut. When activated at one approved alignment point, it freezes only actors tagged FocusPause for 12 seconds: a loom, a moving gate and one patrol. Rain droplets and machinery should receive a subtle cold silver-blue effect, but the player remains free. It can be used once in this level. On timeout all prior velocity, route state and light behavior must restore safely. Give implementation steps, actor tags, events and failure tests.
```

### Chess finale

```text
[Paste Universal context]

Design BP_ChessFinal as a preset three-choice interaction, not chess AI. The player can select exactly one of three marked pieces: BlockExit, OpenDiagonal or ExposePiece. Each selection writes EscapeChoice into BP_GameProgress and launches a corresponding 15–25 second active escape route. All routes converge at the same farewell sequence. Explain the actor setup, input state, camera setup, one test per choice and how to prevent replaying the interaction.
```

## 4. Characters and facial acting

### Recommended route

Create both people as MetaHumans after the jam begins. Use MetaHuman and Unreal Sequencer/Control Rig for close-ups; Epic documents direct Control Rig animation inside Sequencer, including its facial rig. genui{"citation":{"refs":["turn854070447search0","turn854070447search1","turn854070447search9"]}}

Do not spend Meshy credits on the two leads unless the MetaHuman route fails. Generated human models create avoidable rigging, face and clothing problems.

### Protagonist creation brief

```text
Fictional young adult, fair skin, androgynous silhouette, very short dense dark curly crop with compact crown volume and a short irregular fringe. Sides and nape closely cropped. Calm observant eyes, not a copied real person. Clothing: charcoal hoodie with visible hood, comfortable fitted silhouette, dark utility pants, tiny black wireless earbuds, no backpack, no jacket, no large headphones. Same height as the Visitor.
```

### Visitor creation brief

```text
Fictional young adult, fair skin, same height as the protagonist, dark brown hair at shoulder length with relaxed natural waves. Warm direct expression, practical long charcoal coat, dark trousers and boots, one small muted amber scarf detail. No weapon, no villain styling, no glamorous outfit.
```

### Facial performance inside Unreal

Do not attempt full performance capture first. Use Face Control Rig keys in Sequencer for four small performances:

| Shot | Length | Face and body direction |
|---|---:|---|
| Cut reaction | 2 s | Eyes widen, breath catches, shoulders pull back, then look toward the new world. |
| Dragon grip | 3 s | Jaw set, brow tight, head lowered against wind, both hands lock on the saddle/neck strap. |
| Chess recognition | 2 s | Eyes hold on Visitor, brow softens, smallest exhale; no large smile. |
| Farewell | 2 s | Look over Visitor's shoulder, half-smile, eyes return to board. |

Use body locomotion loops for running/walking. For a single difficult body pose, keyframe only the opening and closing pose in Control Rig; hide the midpoint with a camera cut or motion blur.

### Rokoko text-to-motion prompts

Use Rokoko only for one or two body clips if the export works in your setup. Rokoko supports video/text-to-motion workflows and Unreal integration, but keep it as an enhancement rather than a dependency. genui{"citation":{"refs":["turn854070447search11","turn854070447search17","turn854070447search32"]}}

```text
Prompt 01 — Dragon grip
Young adult rider on a large flying creature, bracing against violent wind, both hands gripping a front harness, knees bent, one controlled stumble forward, head ducked, determined recovery. Three seconds, seamless loop, no weapon.

Prompt 02 — Chess rise
Young adult stands slowly from a chair after an unfinished chess game, one hand briefly touches the table, turns toward an exit, pauses without looking back. Three seconds, restrained natural acting.

Prompt 03 — Factory sprint
Young adult runs across a wet industrial floor, glances toward a closing gate, makes one short side-step and continues. Two seconds, loop-friendly, no weapon.
```

### iClone

iClone Personal has a 30-export limit for FBX/OBJ/ABC/USD. Do not make it a mandatory pipeline on day one. Use it only if you already have the two character meshes and need to clean one finished animation late in production. genui{"citation":{"ref":"turn854070447search35"}}

## 5. 3D asset generation prompts

Generate final assets only after the jam begins. Always import one candidate, check scale, collision, material slots and silhouette in Unreal, then decide whether to regenerate.

### Dragon — Rodin first, Meshy fallback

```text
Original fantasy storm dragon for a third-person Unreal Engine game. Long elegant silhouette, slate charcoal scales with subtle cool silver edges, broad leather-like wings, no saddle, no armor, no rider, no fire breath, no horns shaped like a known franchise character. The camera sees it mostly from behind and below during flight. Build-ready game asset: clean quad topology, separated wings, readable neck and back grip area, PBR textures, one material set, medium polycount, neutral A-pose flight posture, no environment, transparent or plain background.
```

Acceptance: readable silhouette at distance; protagonist can be attached at one named socket; no visible logo; no broken wings; does not need facial animation or combat.

### White chess knight

```text
Worn white ceramic chess knight, original design, small carved spiral detail at the base, one hairline crack, matte ivory glaze, emotional keepsake rather than luxury object. Game-ready hero prop for Unreal Engine: centered pivot at base, clean topology, PBR base color/roughness/normal maps, no text, no logos, isolated object, realistic 12 cm tabletop scale.
```

### Silver war seal

```text
Small original medieval silver insignia for a narrative game, a circular seal with a simple abstract wing-and-path symbol, rain-worn metal, shallow engraved grooves, no letters, no recognizable heraldry, no real-world logo. Game-ready prop for Unreal Engine: centered pivot, clean topology, one PBR material, readable silhouette at close range, isolated object.
```

### Factory control panel if needed

```text
Abandoned textile-factory crane control panel, compact steel housing, one large hand wheel, two push buttons, cable conduit and a small circular recess designed to receive a silver seal. Wet rust, faded industrial paint, no readable labels, no logo, game-ready PBR asset, centered pivot, isolated object.
```

## 6. PBRgen material prompts

```text
Material 01 — Wet textile factory steel
Seamless PBR material: dark oxidized steel with damp rain streaks, cold blue-gray reflected light, subtle rust around seams, no text, no decals. Generate base color, normal, roughness, metallic and ambient occlusion maps. 2K tileable.

Material 02 — Damp industrial fabric
Seamless PBR material: aged woven cotton factory cloth, off-white to cool gray, damp edges, small tears and fraying only in normal/albedo detail, no blood, no writing. 2K tileable.

Material 03 — Battlefield mud and grass
Seamless PBR material: rain-soaked dark soil, trampled grass, puddle edges and small stones, cold overcast color, no bodies, no weapons, no tracks with logos. 2K tileable.

Material 04 — Cliff basalt
Seamless PBR material: wet dark basalt cliff with pale mineral veins and moss in cracks, cold blue-gray rain lighting, no snow, no text. 2K tileable.
```

## 7. Sequencer shot prompts

Use these as a shot list for Sequencer, not as extra cinematic work.

```text
Dragon entry: 2 seconds. Tight close-up on protagonist's startled eyes in the factory. Match-cut a circular lamp to a lightning flash. Camera pulls back as she grabs the dragon harness. Return control immediately.

War entry: 2 seconds. Camera starts on silver factory seal, cuts to the same shape on a battlefield shrine. Protagonist is already crouched behind a low wall as patrols cross the field. Return control.

Cliff entry: 2 seconds. Protagonist stumbles forward onto a wet cliff edge. Hold her frightened face for half a second, then pan toward invisible platforms revealed by a pale blue aura. Return control.

Hospital echo: 12 seconds maximum. Quiet room, rain on window, two children playing chess. The extroverted child points at the white knight. No dialogue, no injury, no explanation. Cut to adult chessboard on the same knight.

Chess farewell: 8 seconds. Patrol light approaches in background. Visitor rises. Protagonist looks slightly above Visitor's shoulder, smiles only a little, returns gaze to the board. Visitor leaves frame. Hold on white knight for one second.
```

## 8. Audio brief

All final dialogue must be English. Keep dialogue minimal.

```text
Visitor line 01: “You arrived sooner than I expected.”
Visitor line 02: “Not everything they protect deserves to stay locked away.”
Visitor line 03: “Someone is waiting for me. I am not leaving empty-handed.”
Visitor line 04: “Do not move that piece. I want to know exactly where I left it.”
```

Music direction for an original generator or composer:

```text
Original instrumental score for a short Unreal narrative game. Five-note motif, no lyrics, no recognizable melody or copyrighted reference. Cold rain-soaked piano and distant strings for factory; urgent low percussion for battlefield; high wind textures for cliff; restrained intimate piano for chess. Must loop cleanly and leave room for sound effects.
```

## 9. Asset decision gate

Before spending credits, answer all four questions:

1. Is the prop visible in a close-up, the 30–60 second video, or a defining mechanic?
2. Cannot a primitive, Fab/Quixel asset or material solve it in under 20 minutes?
3. Does it have a fixed gameplay location and collision requirement?
4. Is there enough time to import and test it today?

If any answer is no, do not generate it yet.

## 10. Submission checklist

- Package a Windows build; never submit an unpackaged Unreal project.
- Record 30–60 seconds of 1920×1080 or higher gameplay.
- Keep in-game text, voice, subtitles, itch description and video captions in English.
- Declare sourced assets, tools used, licenses and final AI-generated assets.
- List Rodin if the dragon is used, and retain prompts plus Git history.
- Submit manually as the team owner; no automated submission.
