# The Unfinished Move — Playability Canon

**This is the authoritative gameplay contract.** Every Claude Code agent, Cursor task and implementation prompt must read it with `JAM_COMMAND_CENTER.md` and `JAM_PROMPT_PACK.md`. If another early planning document conflicts with this file, this file wins.

## The promise

The game is not a walking simulator or a sequence of trailers. The player constantly **changes the edit of the world**. Director’s Cut is a playable verb, not an explanation in dialogue.

## Three verbs only

| Verb | Input/reading | Player purpose | Rule |
|---|---|---|---|
| **Match Cut / Reframe** | Player moves camera until two deliberately visible visual shapes align; a cold silver stitch flashes. | Reveal/change a physical route, reveal safe cover, or enter a pocket cut. | Never be a generic “press interact on glowing object.” It has an obvious composition clue and immediate physical payoff. |
| **Cut Boost** | Short directional impulse with a clear cooldown/VFX. | Dodge, cross a gap, reach a current or execute a route at speed. | One reusable implementation across all scenes; no stamina, combat or upgrade tree. |
| **Focus Cut** | One-use 12-second local pause after the cliff lesson. | Freeze tagged machinery, a gate or a patrol while player traverses. | Player remains active. Frozen actors restore safely. |

## Rhythm laws

1. There must be a decision, danger, discovery or input challenge at least every **15–20 seconds**. No empty corridors longer than this.
2. Every 30 seconds asks at least one of: **which route**, **when to use ability**, **can I execute the timing**.
3. Every cut shows its objective, danger and finish in the first five seconds through composition, not a tutorial text panel.
4. Failure is soft: checkpoint 3–5 seconds back, never a Game Over screen or long replay.
5. Cinematic control lock is 1–3 seconds at cut entries/exits. Hospital echo is max 12 seconds. Farewell is max 8 seconds.
6. A new scene does not introduce a new control. It remixes Reframe, Boost or Focus Cut.

## Scene contracts

| Scene | Minute-to-minute challenge | Minimum active decisions | Factory consequence |
|---|---|---|---|
| **Factory** | Choose cover/distraction, find a Match Cut angle, execute a Boost over a small route hazard. | Patrol route versus fabric cover; when to frame; when to Boost. | The factory is altered visibly, not just a door silently unlocked. |
| **Dragon** | Guided, three-lane aerial traversal. Steer through visible currents, avoid 3 obstacle beats, Boost at marked current gaps. | Choose lane; react to obstacle; time Boost. | High catwalk/vertical path gains accessibility. No free flight or dragon combat. |
| **War** | Open field with three readable non-combat routes: safer cover, quicker wagons/trench, or risky mud/Boost route. Use contextual sword only on one marked rope. | Choose route; duck/evade moving threat; choose Boost timing. | Player gets silver seal and can operate crane/fabric bridge. |
| **Cliff** | Camera angle reveals temporary platforms; player crosses before they fade using Boost. | Search frame; commit to platform; time Boost. | Awards Focus Cut. Keep map compact; it is a precision lesson, not a scenic walk. |
| **Chess escape** | Three pieces select a temporary factory condition, then player moves through the same compact escape arena. | Choose which learned verb helps Visitor; execute it under patrol pressure. | The choice has a visible consequence before the farewell. |

## Chess choices: one arena, different active solve

| Piece | Factory state | Player action |
|---|---|---|
| **Block Exit** | Visitor takes a dangerous broken catwalk. | Boost to reach and activate temporary crane/fabric bridge. |
| **Open Diagonal** | Patrol blocks the direct line. | Reframe a light/machine to distract it and open the diagonal. |
| **Expose Piece** | A low hatch is the only route. | Spend Focus Cut to freeze the gate/loom and open it. |

All routes converge after 15–25 seconds. Do not build three separate maps, endings or cutscenes.

## Definition of “fun enough”

A playtester can explain, without reading text: “I was changing the shot to change the route. Then I learned a move in a fantasy scene and used it back in the factory.” If they only say “I walked and watched cool scenes,” the build fails this canon.

## Scope guard

If a proposed feature does not strengthen one of the three verbs or one of the five scene contracts, cut it. A completed 8–10 minute version with Dragon and War is stronger than an unfinished 16-minute version. Cliff may become a compact 25–45 second precision lesson if necessary, but never removes its Focus Cut payoff.
