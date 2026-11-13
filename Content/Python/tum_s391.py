# Real sword clashes (CC0 StarNinjas recordings) with distance falloff, calmer duel rhythm; stony ground at native texture scale (no stretching)
import unreal, importlib, traceback, math, random, inspect
import tum_graph as TG; importlib.reload(TG)
import tum_s324 as T; importlib.reload(T)
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; SW = f"{R}/Audio/SFX/Sword"; MS = "/Game/MS/3D"
SRC = r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\audio\sfx\starninjas"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]

def sounds():
    tasks = []
    for f in [f"SFX_Clash_{i}" for i in range(1, 11)] + [f"SFX_Swing_{i}" for i in range(1, 7)]:
        t = unreal.AssetImportTask(); t.filename = rf"{SRC}\{f}.wav"; t.destination_path = SW; t.automated = True; t.save = True; t.replace_existing = True; tasks.append(t)
    AT.import_asset_tasks(tasks)
    ap = f"{SW}/ATT_Battle"
    att = EAL.load_asset(ap) if EAL.does_asset_exist(ap) else AT.create_asset("ATT_Battle", SW, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    s = att.get_editor_property("attenuation")
    s.set_editor_property("falloff_distance", 2600.0)
    try: s.set_editor_property("attenuation_shape_extents", V(250, 0, 0))
    except Exception: pass
    att.set_editor_property("attenuation", s); EAL.save_loaded_asset(att, False)
    n = 0
    for f in [f"SFX_Clash_{i}" for i in range(1, 11)] + [f"SFX_Swing_{i}" for i in range(1, 7)] + ["../SFX_StoneImpact", "../SFX_CatapultLaunch"]:
        p = f"{SW}/{f}" if not f.startswith("..") else f"{R}/Audio/SFX/{f[3:]}"
        w = EAL.load_asset(p)
        if w:
            w.set_editor_property("attenuation_settings", att)
            try: w.set_editor_property("volume", 0.8 if "Clash" in f else 1.0)
            except Exception: pass
            EAL.save_loaded_asset(w, False); n += 1
    return n

def duel_bp():
    import tum_s321 as H; importlib.reload(H)
    src = inspect.getsource(H.duel)
    src = src.replace(":Min 0.8 :Max 1.6", ":Min 1.6 :Max 2.8")
    src = src.replace(":VolumeMultiplier 0.5 :PitchMultiplier (Math|Random|RandomFloatinRange :Min 0.8 :Max 1.25))",
                      ":VolumeMultiplier 0.7 :PitchMultiplier (Math|Random|RandomFloatinRange :Min 0.92 :Max 1.08))")
    src = src.replace("(< (Math|Random|RandomFloatinRange :Min 0.0 :Max 1.0) 0.3)", "(< (Math|Random|RandomFloatinRange :Min 0.0 :Max 1.0) 0.25)")
    ns = dict(H.__dict__); exec(src, ns); return ns["duel"]()

def assign():
    clashes = [EAL.load_asset(f"{SW}/SFX_Clash_{i}") for i in range(1, 11)]
    swings = [EAL.load_asset(f"{SW}/SFX_Swing_{i}") for i in range(1, 7)]
    n = 0
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("Duel2_") and not lab.endswith(("a", "b", "Sword")):
            a.set_editor_property("Clang", random.choice(clashes)); a.set_editor_property("Shout", random.choice(swings)); n += 1
        if lab.startswith("Knight_") and not lab.endswith(("Body", "Sword")):
            a.set_editor_property("Clang", random.choice(clashes)); n += 1
        if lab in ("Battle_Ambience",):
            ac = a.get_component_by_class(unreal.AudioComponent); ac.set_volume_multiplier(0.45)
    return n

def ground():
    random.seed(31)
    rough = T.sms(f"{MS}/Rocky_Forest_Path_vefhef2ga") + T.sms(f"{MS}/Nordic_Beach_Rocky_Ground_ve3qdhmqx") + T.sms(f"{MS}/Nordic_Beach_Rocky_Ground_vf5pajccb") + T.sms(f"{MS}/Nordic_Beach_Rocky_Ground_ukoncdamw")
    nat = {}
    for m in rough:
        b = m.get_bounding_box(); nat[m.get_name()] = max(b.max.x - b.min.x, b.max.y - b.min.y)
    removed = 0
    for a in list(E.get_all_level_actors()):
        if str(a.get_folder_path()).startswith("Art/War/GroundTiles"):
            l = a.get_actor_location()
            if -900 < l.x < 7200 and -4700 < l.y < 4700: E.destroy_actor(a); removed += 1
            else:
                # far tiles: keep but cap the stretch at 2x native
                m = a.static_mesh_component.static_mesh; s = a.get_actor_scale3d()
                if s.x > 2.0: a.set_actor_scale3d(V(2.0, 2.0, min(s.z, 1.4)))
    n = 0
    step_ = 175.0
    x = -800.0
    while x < 7100:
        y = -4600.0
        while y < 4600:
            m = random.choice(rough)
            a = E.spawn_actor_from_object(m, V(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360)))
            s = random.uniform(0.9, 1.25); size = nat[m.get_name()] * s
            a.set_actor_scale3d(V(s, s, s * random.uniform(0.6, 0.9)))
            o, e = a.get_actor_bounds(False); l = a.get_actor_location()
            px, py = x + random.uniform(-50, 50), y + random.uniform(-50, 50)
            a.set_actor_location(V(l.x + px - o.x, l.y + py - o.y, l.z + 4 - (o.z + e.z) + e.z * 0.35), False, False)
            a.set_actor_enable_collision(False); a.static_mesh_component.set_cast_shadow(False)
            a.set_actor_label(f"GT2_{n}"); a.set_folder_path("Art/War/GroundTiles"); n += 1
            y += min(step_, size * 0.7)
        x += step_
    # soil between: small tiling so it never smears
    mi = EAL.load_asset(f"{R}/Materials/Surfaces/MI_War_Soil")
    try:
        unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi, "TileSize", 260.0); EAL.save_loaded_asset(mi, False)
    except Exception: pass
    return {"removed": removed, "tiles": n, "native": {k: round(v) for k, v in nat.items()}}

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("sounds", sounds); step("duel", duel_bp); step("assign", assign); step("ground", ground)
    L.save_current_level()
    return res
