# Soldiers face where they move: Meshy run clips are turned 180 deg vs walk/crouch/fight clips, so the body yaw is set per clip.
# Run clips: body relative yaw +90. Every other clip: -90.
import unreal, importlib, inspect, traceback
import tum_graph as TG; importlib.reload(TG)
import tum_s364b as S; importlib.reload(S)
import tum_s500 as P; importlib.reload(P)
EAL = unreal.EditorAssetLibrary; E = S.E; L = S.L
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
RUNS = ("soldier3Running", "soldier3RunFast", "soldier3Run_02")
def turn(mod_g, var, anim):
    yaw = 90 if "Run" in anim else -90
    return f"(Transformation|SetActorRelativeRotation :self {mod_g(var)} :NewRelativeRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw {yaw}.0))"

def knight():
    real = importlib.reload
    def rl(m):
        m = real(m)
        if m.__name__ == "tum_s394":
            old = m.play
            m.play = lambda var, anim, loop="true": old(var, anim, loop) + "\n      " + turn(m.g, var, anim)
        return m
    importlib.reload = rl
    try: return P.knight_bp()
    finally: importlib.reload = real

def wanderer():
    src = inspect.getsource(S.wanderer)
    ns = dict(S.__dict__); old = S.play
    ns["play"] = lambda var, anim, loop="true": old(var, anim, loop) + "\n        " + turn(S.g, var, anim)
    exec(src, ns); return ns["wanderer"]()

def level():
    out = {"k": 0, "w": 0, "free": 0}
    handled = set()
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if (lab.startswith("Knight_") or lab.startswith("Wander_")) and not isinstance(a, (unreal.SkeletalMeshActor, unreal.StaticMeshActor)):
            b = a.get_editor_property("Body")
            if not b: continue
            an = b.skeletal_mesh_component.get_editor_property("animation_data").get_editor_property("anim_to_play")
            yaw = 90 if (an and an.get_name() in RUNS) else -90
            b.root_component.set_relative_rotation(unreal.Rotator(roll=0, pitch=0, yaw=yaw), False, False)
            handled.add(b.get_path_name()); out["k" if lab.startswith("Knight") else "w"] += 1
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.SkeletalMeshActor) and a.get_path_name() not in handled:
            m = a.skeletal_mesh_component.get_skeletal_mesh_asset()
            if m and "/War/Soldiers/" in m.get_path_name():
                an = a.skeletal_mesh_component.get_editor_property("animation_data").get_editor_property("anim_to_play")
                if not (an and an.get_name() in RUNS):
                    r = a.get_actor_rotation(); a.set_actor_rotation(unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=r.yaw + 180), False); out["free"] += 1
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_WarField")
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("TMP_"): E.destroy_actor(a)
    step("knight", knight); step("wanderer", wanderer); step("level", level)
    return res
