# Game Brief: La partida pendiente

## In your words

La protagonista entra voluntariamente a una ciudad imaginaria por las noches. Tiene una vida real normal y sabe distinguir ambos lugares. En la ciudad pertenece a un grupo que protege objetos; una joven extrovertida ha entrado en una fábrica abandonada para tomar uno de ellos. La protagonista la sigue, aunque no entiende por qué le resulta familiar.

La fábrica es el presente y el **corte oficial** de la historia. Al acercarse a la visitante o tocar objetos-ancla, la protagonista cae en **cortes vividos**: escenas fantásticas que imaginó durante distintos momentos de su crecimiento. No son multiversos ni niveles aleatorios. Son películas internas que está viviendo de nuevo, con miedo, para descubrir cómo avanzar en la fábrica y quién es la visitante.

**Pitch:** A quiet guardian chases a familiar intruder through an abandoned factory, falls into three playable lost scenes—a dragon flight, a medieval siege, and a luminous cliff—and returns to a secret chess game that reveals their unfinished connection.

**Genre:** Third-person playable cinematic trailer: narrative action-platforming and environmental puzzle game.

**Controls:** Keyboard and mouse or gamepad. Move, look, interact, activate Cut, use a universal Cut Boost, and choose one preset chess move.

**Question:** Can short, playable fantasy scenes make the player feel that they are reconstructing the protagonist’s personal Director’s Cut rather than simply watching flashbacks?

**Hooks:** A visibly lived transition from realistic factory to dragon flight; the same movement ability changes its fantasy costume in every cut; a secret chess meeting between two people on opposing sides.

**Intent:** a 12–18 minute game that feels like a spectacular trailer the player controls. It must be coherent without long text, dialogue trees, combat systems, or a full open city.

## Look and references

- **Look:** semi-realistic 3D Unreal cinematic. The factory is rain-soaked, industrial, blue and amber. Cuts use stronger genre color: cloud-white/fire-orange for dragon flight, mud-red/gold for medieval war, soft dawn/teal for the cliff. The factory remains the visual DNA of every cut.
- **Protagonist:** young adult woman; short dense dark curls, volume on top, close sides; oversized dark jacket and headphones. Never render her with long hair.
- **Visitor:** young adult woman in a structured dark coat with a restrained amber accent. Warm, direct, not villainous.
- **View:** close third person during gameplay; 1–3 second Sequencer camera takeovers at every cut entrance and exit.
- **References:** original genre language only. Never recreate copyrighted films, games, characters, music, symbols, or named worlds.

## First minute

The player sees the protagonist in her real bedroom. She puts on headphones and enters the factory by a visual match cut. The visitor runs through the rain-lit floor. The player follows, touches a circular lamp, sees a close-up of the protagonist’s frightened adult face, hears a dragon roar, and abruptly regains control while clinging to a dragon above clouds.

## Challenge

The visitor is always one step ahead in the factory. Each time she reaches an inaccessible route, the player finds an anchor and enters a short lost scene. Completing the scene gives a visual answer and changes the factory’s next route. The player is not collecting lore: every cut must solve a physical path problem.

## Core loop

1. Follow the visitor in the factory.
2. Encounter a blocked path or impossible route.
3. Find an object-ancla and activate a Cut.
4. Experience a 60–90 second fantasy set piece with one goal and one danger.
5. Return to the exact factory checkpoint with a route, clue, or powered mechanism unlocked.
6. Advance the chase and recover another piece of the visitor’s identity.

## The three cuts

| Cut | Player action | Factory payoff | Emotional image |
|---|---|---|---|
| Dragon flight | Guided flight through three light currents; dodge debris/fire. | Reveals the upper catwalk route. | A younger silhouette makes the same reaching gesture. |
| Medieval siege | Use the Cut Boost as a sword-dash to cross rubble and activate a beacon. | Powers an industrial lamp/door. | A teenage version watches someone leave through banners. |
| Luminous cliff | Follow an amber aura; reveal temporary platforms by looking/alignment. | Finds the white knight and access to the central nave. | The aura briefly becomes the knight/child’s outline. |

## Goal & failure

Reach the central nave before the guards close the factory. Soft failure only: falling or missing a set-piece route returns the player to that cut’s last checkpoint. Complete the final scripted chess exchange; the visitor leaves and the game returns to the real morning.

## Features

- [ ] Real bedroom opening and real-world epilogue.
- [ ] Rainy factory hub with three checkpoints.
- [ ] Three short playable cuts: dragon, siege, cliff.
- [ ] One reusable Cut Boost with different VFX/animation language per scene.
- [ ] Short hospital/chess image integrated into final reveal, not a fourth level.
- [ ] Scripted chess interaction and 40-second departure cinematic.

## Your systems

- `BP_CutAnchor` · Starts a specific cut and owns its checkpoint.
- `BP_CutSequenceManager` · Plays entry/exit shot, loads/teleports to pocket scene, returns player safely.
- `BP_CutBoost` · Universal dash/impulse; uses different VFX per cut.
- `BP_VisitorDirector` · Moves the visitor along fixed factory beats.
- `BP_GameProgress` · Opens routes after each cut.
- `BP_ChessFinal` · Preset move selection and cinematic triggers.

## Keep

- The factory as the current, secret location of the story.
- The protagonist’s silence, gaze and chess moves as valid dialogue.
- The visitor’s urgency without a villain monologue.
- The adult protagonist reacting with fear when a cut begins.
- The final moment: she looks above the visitor’s shoulder, smiles slightly, then returns to the board.

## Avoid

- No multiverse explanation.
- No full combat, free flight, chess AI, enemy AI, dialogue tree, open world, inventory, procedural generation or long flashback cinematics.
- No clinical labels, explicit trauma, gore, horror glitches, direct romance confirmation or borrowed IP.

## Out of scope

- The visitor’s father, the full guardian group conflict and the origin of every imagined story belong to the future game.
- The jam only proves that the visitor has existed across the protagonist’s life and that the protagonist now chooses to protect the unfinished connection.

## Build order

1. Graybox factory, visitor placeholder, one Cut entry/return and universal boost.
2. Build dragon cut completely from entry to factory payoff.
3. Reuse the cut framework for siege and cliff.
4. Add final chess, real-world bookends, lighting, sound and performance polish.

---

**Kill condition:** If a cut cannot be completed in 90 seconds or needs an explanatory text box, simplify its route and make the visual clue larger.

**Who it’s for / what they feel:** Players who want the rush of controlling a cinematic trailer but leave with the quiet sense that every spectacular role was a younger version of the same person trying to find someone familiar.
