# War patch: ruins sized by height, real fires (Niagara), smoke, brighter dusk
import unreal, random, importlib
import tum_s195 as W; importlib.reload(W)
EAL = unreal.EditorAssetLibrary; E = W.E; V = unreal.Vector
def niag(path, name, x, y, z, scale=1.0, folder="Art/War/Fire"):
    ns = EAL.load_asset(path)
    a = E.spawn_actor_from_object(ns, V(x, y, z), unreal.Rotator())
    a.set_actor_scale3d(V(scale, scale, scale)); return W.label(a, name, folder)
def resize_ruins():
    random.seed(9)
    n = 0
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("Ruin_") and isinstance(a, unreal.StaticMeshActor):
            m = a.static_mesh_component.static_mesh; b = m.get_bounding_box(); ext = b.max - b.min
            h = random.uniform(260, 480); s = h / max(ext.z, 1)
            a.set_actor_scale3d(V(s, s, s)); n += 1
    return n
def fires():
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label()
        if lab.startswith(("Fire_Logs", "Fire_FX", "Fire_Embers", "Battle_Smoke")): E.destroy_actor(a)
    beam = W.sm(f"{W.MS}/Worn_Wooden_Beam_tgmsdc0fa/SM_Worn_Wooden_Beam_tgmsdc0fa_00_N1"); ext = beam.get_bounding_box().max - beam.get_bounding_box().min
    s = 260.0 / max(ext.x, ext.y, ext.z)
    random.seed(5); out = 0
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label()
        if not lab.startswith("Fire_Glow"): continue
        l = a.get_actor_location(); i = lab.split("_")[-1]
        a.set_actor_location(V(l.x, l.y, 120), False, False)
        a.point_light_component.set_intensity(18000.0); a.point_light_component.set_attenuation_radius(1600.0)
        for k in range(3):
            yaw = random.uniform(0, 360)
            b = E.spawn_actor_from_object(beam, V(l.x + random.uniform(-40, 40), l.y + random.uniform(-40, 40), 15), unreal.Rotator(roll=random.uniform(-10, 10), pitch=90, yaw=yaw))
            b.set_actor_scale3d(V(s, s, s)); b.set_actor_enable_collision(False); W.label(b, f"Fire_Logs_{i}_{k}", "Art/War/Fire")
        niag("/Game/Effects/Flames/NS_FireLarge", f"Fire_FX_{i}", l.x, l.y, 20, 1.0)
        niag("/Game/Effects/Embers/NS_EmbersLarge", f"Fire_Embers_{i}", l.x, l.y, 80, 1.0)
        out += 1
    for i, (x, y) in enumerate(((1200, 5200), (4200, 6000), (6800, 4200), (2600, -5600), (6000, -6200), (-1200, -4800), (8200, 1000), (-2500, 2000))):
        niag("/Game/Effects/NS_SmokeBillow", f"Battle_Smoke_{i}", x, y, 0, random.uniform(2.5, 4.0))
    return out
def light():
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "Sun":
            a.light_component.set_intensity(7.0)
        if isinstance(a, unreal.SkyLight): a.light_component.set_intensity(1.4); a.light_component.recapture_sky()
        if isinstance(a, unreal.PostProcessVolume):
            s = a.settings; s.set_editor_property("override_auto_exposure_bias", True); s.set_editor_property("auto_exposure_bias", 1.2); a.settings = s
    return "ok"
def run():
    res = {}
    for n, f in (("ruins", resize_ruins), ("fires", fires), ("light", light)):
        try: res[n] = f()
        except Exception as e:
            import traceback; res[n] = traceback.format_exc()[-800:]
    W.L.save_current_level(); return res
