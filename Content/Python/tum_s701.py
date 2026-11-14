# Dragon obstacles as a slalom for a wide-winged dragon: one rock spur at a time, alternating sides, each leaving a passage
# wider than the wingspan. Spurs are rebuilt to fill the blockers exactly and still grow from the water into the canyon wall.
import unreal, traceback
import tum_s291 as D
import tum_s679 as W
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); V = unreal.Vector
MS = "/Game/MS/3D"; SEA = 0.0; F = "Art/Dragon/Canyon"
# label -> (x, side, inner |y|)
PLAN = {"StormWall_0": (2650, 1, 430), "StormWall_1": (5650, -1, 430), "StormWall_2": (8700, 1, 380), "StormWall_3b": (9700, -1, 380)}
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def apply():
    out = {}
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Spur_"): E.destroy_actor(a)
    huge = D.sms(f"{MS}/Huge_Nordic_Coastal_Cliff_ulkiejkva") + D.sms(f"{MS}/Huge_Nordic_Coastal_Cliff_venrdcgga") + D.sms(f"{MS}/Nordic_Coastal_Cliff_ulmiccava")
    stacks = D.sms(f"{MS}/Nordic_Beach_Rock_Formation_vd4iecjva") + D.sms(f"{MS}/Nordic_Beach_Rock_Formation_vckqccbga") + D.sms(f"{MS}/Nordic_Beach_Rock_Formation_vfgkajyga")
    cands = huge + stacks; nat = {}
    for m in cands:
        t = E.spawn_actor_from_object(m, V(0, 0, -50000), unreal.Rotator()); o, e = t.get_actor_bounds(False); nat[m.get_name()] = (max(e.x, 1), max(e.y, 1), max(e.z, 1)); E.destroy_actor(t)
    n = 0; dist = []; boxes = {}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab not in PLAN: continue
        x, side, inner = PLAN[lab]; o, e = a.get_actor_bounds(False); sc = a.get_actor_scale3d(); l = a.get_actor_location()
        want_ey = (1150.0 - inner) / 2; a.set_actor_scale3d(V(sc.x, sc.y * want_ey / max(e.y, 1), sc.z))
        o, e = a.get_actor_bounds(False); l = a.get_actor_location()
        a.set_actor_location(V(l.x + x - o.x, l.y + side * (inner + want_ey) - o.y, l.z), False, False)
        o, e = a.get_actor_bounds(False); boxes[lab] = [[round(v) for v in o.to_tuple()], [round(v) for v in e.to_tuple()]]
        inn = o.y - side * e.y; outer = side * 2450.0; cy = (inn + outer) / 2; ly = abs(outer - inn); bx, bz = 2 * e.x + 60, 3400.0 + 300
        best = None
        for m in cands:
            ex0, ey0, ez0 = nat[m.get_name()]
            for yaw in (0, 90):
                s = (ly / (2 * ex0), bx / (2 * ey0), bz / (2 * ez0)) if yaw == 90 else (bx / (2 * ex0), ly / (2 * ey0), bz / (2 * ez0))
                r = max(s) / min(s)
                if best is None or r < best[0]: best = (r, m, yaw)
        W.fit(best[1], f"Spur_{n}", o.x, cy, SEA - 300, 3400, bx, ly, best[2], F); dist.append(round(best[0], 2)); n += 1
    out["spurs"] = n; out["distortion"] = dist; out["boxes"] = boxes
    L.save_current_level(); return out
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon"); step("apply", apply); return res
