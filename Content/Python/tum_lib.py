# Small level-building helpers for The Unfinished Move (written during the jam).
import unreal
EAS = lambda: unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = lambda: unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary
CUBE = "/Engine/BasicShapes/Cube.Cube"; CYL = "/Engine/BasicShapes/Cylinder.Cylinder"; SPH = "/Engine/BasicShapes/Sphere.Sphere"
GRID = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_Gray.MI_PrototypeGrid_Gray"
GRID_DARK = "/Game/LevelPrototyping/Materials/MI_PrototypeGrid_TopDark.MI_PrototypeGrid_TopDark"
V = unreal.Vector
def R(p=0.0, y=0.0, r=0.0): return unreal.Rotator(roll=r, pitch=p, yaw=y)
def mat(path): return EAL.load_asset(path)
def tag(a, label, folder, tags=()):
    a.set_actor_label(label); a.set_folder_path(folder)
    a.tags = [unreal.Name(t) for t in tags] + [unreal.Name("TUM_Built")]
    return a
def box(label, x0, x1, y0, y1, z0, z1, m=GRID, folder="Graybox", tags=(), mesh=CUBE, collide=True, yaw=0.0):
    a = EAS().spawn_actor_from_object(EAL.load_asset(mesh), V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), R(y=yaw))
    a.set_actor_scale3d(V(abs(x1 - x0) / 100.0, abs(y1 - y0) / 100.0, abs(z1 - z0) / 100.0))
    c = a.static_mesh_component; c.set_material(0, mat(m) if isinstance(m, str) else m)
    if not collide: c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return tag(a, label, folder, tags)
def point(label, x, y, z, folder="Markers", tags=(), yaw=0.0):
    return tag(EAS().spawn_actor_from_class(unreal.TargetPoint, V(x, y, z), R(y=yaw)), label, folder, tags)
def light(label, x, y, z, color=(0.75, 0.85, 1.0), intensity=5000.0, radius=1500.0, folder="Lights", cls=unreal.PointLight, rot=None):
    a = EAS().spawn_actor_from_class(cls, V(x, y, z), rot or R())
    lc = a.get_component_by_class(unreal.LightComponent)
    lc.set_light_color(unreal.LinearColor(*color, 1.0)); lc.set_intensity(intensity)
    try: lc.set_editor_property("attenuation_radius", radius)
    except Exception: pass
    return tag(a, label, folder)
def clear_built():
    n = 0
    for a in EAS().get_all_level_actors():
        if unreal.Name("TUM_Built") in a.tags: EAS().destroy_actor(a); n += 1
    return n
def text(label, x, y, z, s, size=60.0, color=(0.8, 0.85, 0.95), yaw=0.0, folder="Labels"):
    a = EAS().spawn_actor_from_class(unreal.TextRenderActor, V(x, y, z), R(y=yaw))
    t = a.text_render; t.set_text(unreal.Text(s)); t.set_world_size(size); t.set_text_render_color(unreal.Color(int(color[0]*255), int(color[1]*255), int(color[2]*255), 255))
    t.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    return tag(a, label, folder)
def base_lighting(sun_pitch=-35.0, sun_yaw=-60.0, sun=2.0, sky=0.6, fog=0.03, cold=True):
    col = (0.72, 0.82, 1.0) if cold else (1.0, 0.95, 0.85)
    s = EAS().spawn_actor_from_class(unreal.DirectionalLight, V(0, 0, 3000), R(p=sun_pitch, y=sun_yaw))
    lc = s.get_component_by_class(unreal.LightComponent); lc.set_intensity(sun); lc.set_light_color(unreal.LinearColor(*col, 1))
    try: lc.set_editor_property("atmosphere_sun_light", True)
    except Exception: pass
    tag(s, "Sun", "Lighting")
    tag(EAS().spawn_actor_from_class(unreal.SkyAtmosphere, V(0, 0, 0), R()), "SkyAtmosphere", "Lighting")
    sl = EAS().spawn_actor_from_class(unreal.SkyLight, V(0, 0, 500), R()); slc = sl.get_component_by_class(unreal.SkyLightComponent)
    slc.set_editor_property("real_time_capture", True); slc.set_intensity(sky); tag(sl, "SkyLight", "Lighting")
    f = EAS().spawn_actor_from_class(unreal.ExponentialHeightFog, V(0, 0, 0), R()); fc = f.get_component_by_class(unreal.ExponentialHeightFogComponent)
    fc.set_fog_density(fog); fc.set_fog_inscattering_color(unreal.LinearColor(0.35, 0.42, 0.55, 1)); tag(f, "Fog", "Lighting")
    pp = EAS().spawn_actor_from_class(unreal.PostProcessVolume, V(0, 0, 0), R()); pp.set_editor_property("unbound", True); tag(pp, "PP_Global", "Lighting")
    return pp
