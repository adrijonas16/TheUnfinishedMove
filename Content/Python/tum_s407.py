# War: real mountains on the horizon (no washed-out white cliffs), matte rocky soil instead of the wet-looking plane, lighter texture memory
import unreal, importlib, traceback, math, random
import tum_s195 as W; importlib.reload(W)
import tum_s335 as M; importlib.reload(M)
EAL = unreal.EditorAssetLibrary; E = M.E; L = M.L; V = unreal.Vector; MS = "/Game/MS"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def sms(folder):
    try: return [EAL.load_asset(p) for p in EAL.list_assets(folder, False, False) if p.split("/")[-1].startswith("SM_")]
    except Exception: return []

def soil():
    base = (f"{MS}/Surfaces/Rocky_Soil_Ground_vb2qdgwew/T_Rocky_Soil_Ground_vb2qdgwew", f"{MS}/Surfaces/Rocky_Soil_Ground_vb2qdgwew/T_RockySoilGround_vb2qdgwew_ORDp")
    mi = W.tri("MI_War_RockySoil", base, 320.0, (0.78, 0.68, 0.58), 1.6)
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "War_Ground": a.static_mesh_component.set_material(0, mi)
    return mi.get_path_name()

def mountains():
    out = {}
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(("Horizon_Cliff", "Mountain_")): E.destroy_actor(a)
    kinds = sms(f"{MS}/3D/Desert_Western_Cliff_Sheer_Xl_04_xgknben") + sms(f"{MS}/3D/Desert_Western_Cliff_Sheer_Xl_05_xgnlfc0") + sms(f"{MS}/3D/Massive_Nordic_Coastal_Cliff_ullqbb1ga") + sms(f"{MS}/3D/Massive_Nordic_Coastal_Cliff_vdssailfa") + sms(f"{MS}/3D/Huge_Nordic_Coastal_Cliff_ulkiejkva")
    out["kinds"] = [k.get_name() for k in kinds]
    random.seed(99); n = 0
    cx, cy = 3200, 0
    for i in range(16):
        ang = i / 16 * 6.283 + random.uniform(-0.12, 0.12)
        if -0.6 < ang - math.pi < 0.6 and False: continue
        rad = random.uniform(9500, 12500)
        x, y = cx + math.cos(ang) * rad * 1.15, cy + math.sin(ang) * rad
        m = random.choice(kinds)
        a = E.spawn_actor_from_object(m, V(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=math.degrees(ang) + 180 + random.uniform(-25, 25)))
        o, e = a.get_actor_bounds(False); h = random.uniform(2600, 4800); s = h / max(2 * e.z, 1)
        a.set_actor_scale3d(V(s * random.uniform(1.0, 1.6), s * random.uniform(1.0, 1.6), s))
        o, e = a.get_actor_bounds(False); l = a.get_actor_location()
        a.set_actor_location(V(l.x + x - o.x, l.y + y - o.y, l.z - (o.z - e.z) - 300), False, False)
        c = a.static_mesh_component; c.set_collision_profile_name("NoCollision"); a.set_actor_enable_collision(False); c.set_cast_shadow(False)
        a.set_actor_label(f"Mountain_{n}"); a.set_folder_path("Art/War/Horizon"); n += 1
    out["n"] = n
    # fog: keep depth, never wash distant rock to white
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.ExponentialHeightFog):
            f = a.component
            try:
                f.set_fog_density(min(f.fog_density, 0.012)); f.set_editor_property("fog_max_opacity", 0.75)
                f.set_fog_inscattering_color(unreal.LinearColor(0.42, 0.33, 0.26, 1))
            except Exception as ex: out["fog"] = str(ex)
    return out

def texmem():
    n = 0
    for folder in ("/Game/MS/3D/Rocky_Forest_Path_vefhef2ga", "/Game/MS/3D/Nordic_Beach_Rocky_Ground_ve3qdhmqx", "/Game/MS/3D/Nordic_Beach_Rocky_Ground_vf5pajccb",
                   "/Game/MS/3D/Nordic_Beach_Rocky_Ground_ukoncdamw", "/Game/MS/3D/Limestone_Rocks_ubordbyda", "/Game/MS/3D/Limestone_Rubble_ubxbejwda",
                   "/Game/MS/3D/Beach_Rock_wenobjws", "/Game/MS/3D/Cement_Rubble_rinet", "/Game/MS/3D/Desert_Western_Cliff_Sheer_Xl_04_xgknben",
                   "/Game/MS/3D/Desert_Western_Cliff_Sheer_Xl_05_xgnlfc0", "/Game/MS/3D/Massive_Nordic_Coastal_Cliff_ullqbb1ga", "/Game/MS/3D/Massive_Nordic_Coastal_Cliff_vdssailfa",
                   "/Game/MS/3D/Huge_Nordic_Coastal_Cliff_ulkiejkva", "/Game/MS/3D/Beach_Boulder_uisjbbis", "/Game/MS/3D/Beach_Boulder_ukopdins", "/Game/MS/3D/Beach_Boulder_ukopeess",
                   "/Game/MS/3D/Nordic_Beach_Boulder_vcyqebjfa", "/Game/MS/3D/Limestone_Slab_ubxbadpda", "/Game/TUM/War/Soldiers", "/Game/TUM/War/Catapult"):
        try: paths = EAL.list_assets(folder, True, False)
        except Exception: continue
        for p in paths:
            t = EAL.load_asset(p)
            if isinstance(t, unreal.Texture2D):
                cap = 512 if "Cliff" in folder or "Boulder" in folder else 1024
                if t.get_editor_property("max_texture_size") in (0,) or t.get_editor_property("max_texture_size") > cap:
                    t.set_editor_property("max_texture_size", cap); EAL.save_loaded_asset(t, False); n += 1
    return n

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_WarField")
    step("soil", soil); step("mountains", mountains)
    L.save_current_level()
    step("texmem", texmem)
    return res
