import unreal, importlib
import tum_shot as SH; importlib.reload(SH)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); EAL = unreal.EditorAssetLibrary
def run():
    LES.load_level("/Game/TUM/Maps/M_FactoryHub")
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == "Ext_Facade": EAS.destroy_actor(a)
    m = EAL.load_asset("/Game/TUM/Environment/Facade/FBX_1_mln_2x16K_N")
    bb = m.get_bounding_box()
    cx, cy = (bb.min.x + bb.max.x) / 2, (bb.min.y + bb.max.y) / 2
    a = EAS.spawn_actor_from_object(m, unreal.Vector(-762 - cx, -cy, -bb.min.z), unreal.Rotator(0, 0, 0))
    a.set_actor_label("Ext_Facade"); a.set_folder_path("Art/Exterior"); a.tags = [unreal.Name("ArtPass")]
    a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    LES.save_current_level()
    return SH.shots("M_FactoryHub", {"facade_out": ((-6500, 0, 900), (-3, 0), 90), "facade_in": ((500, 0, 900), (-3, 180), 90)})
