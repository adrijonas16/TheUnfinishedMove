import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); EAL = unreal.EditorAssetLibrary
def run(scale=8.0):
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    LES.load_level("/Game/TUM/Maps/M_FactoryHub")
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == "Int_Warehouse": EAS.destroy_actor(a)
    m = EAL.load_asset("/Game/TUM/Environment/Interior/InteriorJoined/StaticMeshes/InteriorJoined"); bb = m.get_bounding_box()
    cx, cy = (bb.min.x + bb.max.x) / 2 * scale, (bb.min.y + bb.max.y) / 2 * scale
    a = EAS.spawn_actor_from_object(m, unreal.Vector(3600 - cx, -cy, -bb.min.z * scale), unreal.Rotator(0, 0, 0))
    a.set_actor_scale3d(unreal.Vector(scale, scale, scale)); a.set_actor_label("Int_Warehouse"); a.set_folder_path("Art/Interior"); a.tags = [unreal.Name("ArtPass")]
    a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    LES.save_current_level()
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-200, 0, 600), unreal.Rotator(roll=0, pitch=-8, yaw=0))
    return [round(v) for v in (bb.min.x * scale, bb.max.x * scale, bb.min.y * scale, bb.max.y * scale, bb.min.z * scale, bb.max.z * scale)]
