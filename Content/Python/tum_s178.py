# Meshy industrial power loom (image-to-3D from our own concept art) dressing every loom cover block
import unreal, importlib
import tum_s107 as S; importlib.reload(S)
import tum_art as A; importlib.reload(A)
EAL = unreal.EditorAssetLibrary; V = unreal.Vector
def E(): return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def imp():
    r = S.import_glb(r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\meshy\IndustrialLoom.glb", "/Game/TUM/Props/Meshy/IndustrialLoom")
    m = EAL.load_asset(r[0]); ns = m.get_editor_property("nanite_settings"); ns.enabled = True; m.set_editor_property("nanite_settings", ns); EAL.save_loaded_asset(m, False)
    for p in EAL.list_assets("/Game/TUM/Props/Meshy/IndustrialLoom", True, False):
        t = EAL.load_asset(p)
        if isinstance(t, unreal.Texture2D): t.set_editor_property("max_texture_size", 2048); EAL.save_loaded_asset(t, False)
    b = m.get_bounding_box(); return r[0], [round(b.max.x - b.min.x), round(b.max.y - b.min.y), round(b.max.z - b.min.z)]
def dress(mesh_path, length=380.0):
    m = EAL.load_asset(mesh_path); b = m.get_bounding_box(); ext = (b.max.x - b.min.x, b.max.y - b.min.y, b.max.z - b.min.z)
    long_is_x = ext[0] >= ext[1]; s = length / max(ext[0], ext[1])
    for a in E().get_all_level_actors():
        if a.get_actor_label().startswith("LoomMachine_"): E().destroy_actor(a)
    n = 0
    for a in E().get_all_level_actors():
        l = a.get_actor_label()
        if (l.startswith("Loom_N") or l.startswith("Loom_S")) and str(a.get_folder_path()).startswith("Graybox"):
            o, e = a.get_actor_bounds(False)
            yaw = 0.0 if long_is_x else 90.0
            if l.startswith("Loom_S"): yaw += 180.0
            x = E().spawn_actor_from_object(m, V(o.x, o.y, -b.min.z * s), unreal.Rotator(roll=0, pitch=0, yaw=yaw)); x.set_actor_scale3d(V(s, s, s))
            x.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            x.set_actor_label(f"LoomMachine_{n}"); x.set_folder_path("Art/Dress/Looms"); x.tags = [unreal.Name("ArtPass")]; n += 1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return n, ext, s
