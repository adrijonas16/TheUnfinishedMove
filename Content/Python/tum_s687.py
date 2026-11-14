# Dragon v2 (after looking at Play screenshots): golden-hour light from behind the rider, canyon rim lower and set back so the
# mountains show, stretched rock bridges replaced by twin rock pinnacles with beacon fires, dragon raised under the rider.
import unreal, importlib, inspect, traceback, random
import tum_s679 as W; importlib.reload(W)
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; D = W.D
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def world():
    src = inspect.getsource(W.world)
    a = "random.uniform(3500, 4700), 200, random.uniform(4200, 5400), random.uniform(180, 650)"
    assert src.count(a) == 1
    src = src.replace(a, "random.uniform(2300, 4300), 200, random.uniform(4200, 5400), random.uniform(350, 1200)")
    i = src.index("    # boost gates = natural rock bridges"); j = src.index("    # goal: a sea stack")
    gates = '''    fire = None
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "Beacon_Fire": fire = a.niagara_component.get_asset()
    for i, gx in enumerate((4030, 7530, 10530)):
        for side in (-1, 1):
            top = random.uniform(2450, 2750)
            D.place(random.choice(stacks), f"GatePillar_{i}_{side}", gx, side * 1800, top, top - SEA + 300, random.uniform(0, 360), F, w=1250)
            if fire:
                fa = E.spawn_actor_from_object(fire, V(gx, side * 1800, top + 40)); fa.set_actor_scale3d(V(2.2, 2.2, 2.2)); fa.set_actor_label(f"GateFire_{i}_{side}"); fa.set_folder_path(F)
'''
    src = src[:i] + gates + src[j:]
    ns = dict(W.__dict__); exec(src, ns); return ns["world"]()
def light():
    out = {}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if isinstance(a, unreal.DirectionalLight):
            c = a.get_component_by_class(unreal.DirectionalLightComponent)
            out["sun_before"] = [str(a.get_actor_rotation()), c.get_editor_property("intensity"), str(c.get_editor_property("light_color"))]
            a.set_actor_rotation(unreal.Rotator(roll=0, pitch=-27, yaw=10), False); c.set_intensity(7.5); c.set_light_color(unreal.LinearColor(1.0, 0.80, 0.60, 1))
        if isinstance(a, unreal.SkyLight):
            c = a.get_component_by_class(unreal.SkyLightComponent); out["sky_before"] = c.get_editor_property("intensity"); c.set_intensity(1.8)
        if isinstance(a, unreal.PostProcessVolume):
            s = a.get_editor_property("settings")
            out["pp_before"] = {k: s.get_editor_property(k) for k in ("override_auto_exposure_bias", "auto_exposure_bias", "override_auto_exposure_min_brightness", "auto_exposure_min_brightness", "auto_exposure_max_brightness")}
            s.set_editor_property("override_auto_exposure_bias", True); s.set_editor_property("auto_exposure_bias", 0.6); a.set_editor_property("settings", s)
        if lab == "Dragon_Mesh":
            l = a.get_actor_location(); out["dragon_before"] = [l.x, l.y, l.z]; a.set_actor_location(V(-7947, 0, -1651), False, False)
        if lab == "Sky_Dome":
            out["sky_dome_mat"] = [m.get_path_name() if m else None for m in a.static_mesh_component.get_materials()]
        if lab.startswith("ShotCam"): E.destroy_actor(a)
    L.save_current_level(); return out
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon"); step("world", world); step("light", light); return res
