# Collision that works in Play: "complex as simple" was never cooked for these meshes, so in Play they had no collision.
# Give each solid prop real simple collision (convex decomposition = tight shape). Make the fog visible as mist.
import unreal, traceback
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SMS = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
L.load_level("/Game/TUM/Maps/M_Cut_WarField")
KEYS = ("Wooden_Crate", "Wooden_Barrel", "Wooden_Beam", "Plank", "Stakes", "Old_Wooden_Pole", "Brick_Walls", "Ruins_Wall", "ChurchRuin",
        "Beach_Boulder", "Nordic_Beach_Boulder", "Limestone_Slab", "CatapultBase", "Rope_Coil", "Dead_Tree")
out = {"meshes": {}, "fog": {}}
seen = set()
for a in E.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor): continue
    m = a.static_mesh_component.static_mesh
    if not m or m.get_name() in seen or not any(k in m.get_name() for k in KEYS): continue
    seen.add(m.get_name())
    try:
        bs = m.get_editor_property("body_setup"); bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
        hulls = 4 if any(k in m.get_name() for k in ("Crate", "Barrel", "Pole", "Boulder", "Slab", "Rope")) else 10
        ok = SMS.set_convex_decomposition_collisions(m, hulls, 24, 300000)
        EAL.save_loaded_asset(m, False)
        out["meshes"][m.get_name()] = [hulls, bool(ok), SMS.get_simple_collision_count(m)]
    except Exception: out["meshes"][m.get_name()] = traceback.format_exc()[-300:]
for a in E.get_all_level_actors():
    lab = a.get_actor_label()
    if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and any(k in a.static_mesh_component.static_mesh.get_name() for k in KEYS):
        a.static_mesh_component.set_collision_profile_name("BlockAll"); a.set_actor_enable_collision(True)
    if isinstance(a, unreal.ExponentialHeightFog):
        fc = a.get_editor_property("component")
        for p in ("fog_density", "fog_height_falloff", "start_distance", "fog_max_opacity", "fog_inscattering_luminance", "enable_volumetric_fog"):
            try: out["fog"][p + "_before"] = str(fc.get_editor_property(p))
            except Exception: pass
        fc.set_editor_property("fog_density", 0.07); fc.set_editor_property("fog_height_falloff", 0.15)
        fc.set_editor_property("start_distance", 0.0); fc.set_editor_property("fog_max_opacity", 1.0)
        try: fc.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.11, 0.125, 0.15, 1.0))
        except Exception: fc.set_editor_property("fog_inscattering_color", unreal.LinearColor(0.11, 0.125, 0.15, 1.0))
        out["fog"]["after"] = "density 0.07 falloff 0.15 grey-blue mist"
L.save_current_level(); RESULT = out
