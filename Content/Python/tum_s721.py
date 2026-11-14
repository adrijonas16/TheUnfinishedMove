# Dragon spurs without stretched rock: each obstacle is a tower of 3-4 uniformly scaled cliff pieces stacked from the water
# up, long side running from the passage into the canyon wall. Blockers widened to the rock's real thickness.
import unreal, random, traceback
import tum_s291 as D
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); V = unreal.Vector
MS = "/Game/MS/3D"; F = "Art/Dragon/Canyon"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def apply():
    random.seed(909); out = {"pieces": 0, "boxes": {}}
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Spur_"): E.destroy_actor(a)
    meshes = [m for m in D.sms(f"{MS}/Huge_Nordic_Coastal_Cliff_venrdcgga") + D.sms(f"{MS}/Massive_Nordic_Coastal_Cliff_ullqbb1ga") if "_03" not in m.get_name()]
    n = 0
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if not lab.startswith("StormWall_"): continue
        o, e = a.get_actor_bounds(False); side = 1 if o.y > 0 else -1; inner = o.y - side * e.y; outer = side * 2450.0
        cy = (inner + outer) / 2; ly = abs(outer - inner); z = -300.0; k = 0; thick = []
        while z < 3250 and k < 5:
            m = random.choice(meshes); yaw = 90 + random.choice((0, 180))
            t = E.spawn_actor_from_object(m, V(0, 0, -60000), unreal.Rotator(roll=0, pitch=0, yaw=yaw)); to, te = t.get_actor_bounds(False); E.destroy_actor(t)
            s = ly / (2 * te.y) * random.uniform(1.0, 1.08); h = 2 * te.z * s
            p = D.place(m, f"Spur_{n}_{k}", o.x + random.uniform(-40, 40), cy, z + h, h, yaw, F); p.set_actor_enable_collision(False)
            thick.append(2 * te.x * s); z += h * 0.8; k += 1; out["pieces"] += 1
        half = min(thick) / 2 * 0.78; sc = a.get_actor_scale3d(); a.set_actor_scale3d(V(sc.x * half / max(e.x, 1), sc.y, sc.z))
        o, e = a.get_actor_bounds(False); out["boxes"][lab] = [[round(v) for v in o.to_tuple()], [round(v) for v in e.to_tuple()], [round(t_) for t_ in thick]]; n += 1
    L.save_current_level(); return out
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon"); step("apply", apply); return res
