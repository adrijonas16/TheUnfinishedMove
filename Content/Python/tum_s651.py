# War pass 5:
# - horses only charge along a clear lane: the whole run (horse -> you, and you -> 22 m past you) is box-checked first;
#   if it is blocked they relocate (out of sight in the fog) and try again
# - camera a bit lower (eye ~1.60 m) and soldiers slightly taller so they read as your size
# - denser fog
import unreal, importlib, inspect, traceback, re
import tum_s645 as T; importlib.reload(T)
import tum_graph as TG
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"; H = T.H; P = T.P
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]

def box(sx, sy, ex, ey):
    return (f"(Collision|BoxTraceByChannel :Start (Math|Vector|MakeVector {sx} {sy} (+ (.z me) 120.0)) :End (Math|Vector|MakeVector {ex} {ey} (+ (.z me) 120.0)) "
            f":HalfSize (Math|Vector|MakeVector 75.0 75.0 90.0) :Orientation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (Math|Trig|Atan2(Degrees) dpy dpx)))")
def lane_transform(code):
    m = re.search(r"\(if \(and \(and \(< \(Variables\|Default\|GetWait\) 0\.0\) \(< dp 4800\.0\)\) \(not (th\d+)\)\)", code)
    if not m: raise RuntimeError("charge-if not found")
    i = m.start(); ls = code.rfind("\n", 0, i) + 1; ind = code[ls:i]
    ux = "(/ dpx (+ dp 1.0))"; uy = "(/ dpy (+ dp 1.0))"
    b1 = box(f"(+ (.x me) (* {ux} 60.0))", f"(+ (.y me) (* {uy} 60.0))", f"(- (.x pl) (* {ux} 150.0))", f"(- (.y pl) (* {uy} 150.0))")
    b2 = box(f"(+ (.x pl) (* {ux} 150.0))", f"(+ (.y pl) (* {uy} 150.0))", f"(+ (.x pl) (* {ux} 2200.0))", f"(+ (.y pl) (* {uy} 2200.0))")
    pre = f"{ind}(bind (ohl1 lane1) {b1})\n{ind}(bind (ohl2 lane2) {b2})\n"
    cond_old = m.group(0); th = m.group(1)
    cond_new = f"(if (and (and (and (< (Variables|Default|GetWait) 0.0) (< dp 4800.0)) (not {th})) (not (or lane1 lane2)))"
    code = code[:ls] + pre + code[ls:i] + cond_new + code[i + len(cond_old):]
    code = code.replace("(if (< (Variables|Default|GetWait) -3.0)", "(if (< (Variables|Default|GetWait) -1.2)")
    return code
_h3 = T.hoist3
def hoist4(code):
    code, n = _h3(code)
    if "GetRun) 7500.0" in code: code = lane_transform(code); res["lane"] = True
    return code, n
def horses():
    TG.ensure_vars(f"{WB}/BP_Cavalry", [("Bumps", "int")])
    H.hoist = hoist4
    from editor_toolset.toolsets import blueprint_dsl
    blueprint_dsl.Transpiler.transpile = H.wrapped
    try: return H.C632.run()
    finally: blueprint_dsl.Transpiler.transpile = H.TRUE_ORIG; H.hoist = P._old_hoist

EYE = 64.0
def camera_and_bob():
    bp = EAL.load_asset(f"{R}/Core/BP_TUMCharacter")
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); F = unreal.SubobjectDataBlueprintFunctionLibrary
    hs = {str(F.get_variable_name(F.get_data(h))): h for h in sds.k2_gather_subobject_data_for_blueprint(bp)}
    boom = F.get_object(F.get_data(hs["CameraBoom"])); boom.set_editor_property("relative_location", V(0, 0, EYE))
    BEL.compile_blueprint(bp); EAL.save_loaded_asset(bp, False)
    src = inspect.getsource(T.headbob).replace("(- 78.0", f"(- {EYE}")
    ns = dict(T.__dict__); exec(src, ns)
    import tum_s612 as T612
    c, k = BT.create_node, BT.connect_pins
    BT.create_node = T.SK._c; BT.connect_pins = T.SK._k; T612.TG.run = T612._run2
    try: return ns["headbob"]()
    finally: T612.TG.run = T612._orig_run; BT.create_node = c; BT.connect_pins = k

def level():
    out = {"scaled": 0}
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.SkeletalMeshActor) and not a.get_actor_label().startswith("Cavalry_"):
            m = a.skeletal_mesh_component.get_skeletal_mesh_asset()
            if m and "/War/Soldiers/" in m.get_path_name():
                s = a.get_actor_scale3d(); a.set_actor_scale3d(V(s.x * 1.06, s.y * 1.06, s.z * 1.06)); out["scaled"] += 1
        if isinstance(a, unreal.ExponentialHeightFog):
            fc = a.get_editor_property("component"); d = fc.get_editor_property("fog_density"); fc.set_editor_property("fog_density", max(d, 0.135)); out["fog"] = [d, max(d, 0.135)]
    return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("horses", horses); step("camera_and_bob", camera_and_bob)
    L.load_level(f"{R}/Maps/M_Cut_WarField"); step("level", level); L.save_current_level()
    return res
