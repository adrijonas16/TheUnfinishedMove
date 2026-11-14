# Walls: replace the single fat box per wall with a grid of thin blockers that follow the real wall footprint
# (scanned with downward traces against the wall's real geometry, 50 cm cells, merged along rows).
import unreal
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; world = unreal.EditorLevelLibrary.get_editor_world()
WALL = ("Brick_Walls", "Ruins_Wall", "ChurchRuin")
cube = EAL.load_asset("/Engine/BasicShapes/Cube"); inv = EAL.load_asset("/Game/TUM/Materials/Surfaces/M_Invisible")
acts = list(E.get_all_level_actors())
for a in acts:
    if a.get_actor_label().startswith("WallCell_"): E.destroy_actor(a)
walls = [a for a in acts if isinstance(a, unreal.StaticMeshActor) and not a.is_hidden_ed() and a.static_mesh_component.static_mesh and any(k in a.static_mesh_component.static_mesh.get_name() for k in WALL)]
wall_ids = {w.get_name() for w in walls}
# remove the fat wall boxes (blockers centred inside wall bounds), and switch off other blockers/tops while scanning
removed = 0; off = []
for a in list(E.get_all_level_actors()):
    lab = a.get_actor_label()
    if lab.startswith("Blocker_"):
        p = a.get_actor_location()
        for w in walls:
            o, e = w.get_actor_bounds(False)
            if abs(p.x - o.x) < 5 and abs(p.y - o.y) < 5:
                E.destroy_actor(a); removed += 1; break
        else:
            a.set_actor_enable_collision(False); off.append(a)
    elif lab.startswith(("WallTop_", "BlockerPole_")):
        a.set_actor_enable_collision(False); off.append(a)
S = 50.0; n = 0
for w in walls:
    o, e = w.get_actor_bounds(False); top = o.z + e.z; bot = o.z - e.z
    xs = [o.x - e.x + S / 2 + i * S for i in range(max(1, int(2 * e.x // S) + 1))]
    ys = [o.y - e.y + S / 2 + j * S for j in range(max(1, int(2 * e.y // S) + 1))]
    for y in ys:
        run_start = None
        for i, x in enumerate(xs + [None]):
            hit = False
            if x is not None:
                r = unreal.SystemLibrary.line_trace_single(world, V(x, y, top + 30), V(x, y, bot - 5), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
                t = r.to_tuple() if r else None
                if t and t[0] and t[9] and t[9].get_name() in wall_ids and t[4].z > bot + 45: hit = True
            if hit and run_start is None: run_start = x
            if not hit and run_start is not None:
                x1 = xs[i - 1]; cx = (run_start + x1) / 2; length = x1 - run_start + S
                b = E.spawn_actor_from_object(cube, V(cx, y, (top + bot) / 2 + 100), unreal.Rotator())
                b.set_actor_scale3d(V(length / 100.0, S / 100.0, (top - bot + 200) / 100.0))
                c = b.static_mesh_component; c.set_material(0, inv); c.set_collision_profile_name("BlockAll"); c.set_cast_shadow(False); c.set_editor_property("hidden_in_game", True)
                b.set_actor_label(f"WallCell_{n}"); b.set_folder_path("Gameplay/WallCells"); n += 1
                run_start = None
for a in off: a.set_actor_enable_collision(True)
# wall tops are now covered by the cells (they rise 2 m above the wall), so remove the old tops
for a in list(E.get_all_level_actors()):
    if a.get_actor_label().startswith("WallTop_"): E.destroy_actor(a)
L.save_current_level(); RESULT = {"walls": len(walls), "fat_boxes_removed": removed, "cells": n}
