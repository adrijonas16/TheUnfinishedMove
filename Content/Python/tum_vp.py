import unreal
def vp(loc, rot):
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(*loc), unreal.Rotator(roll=0, pitch=rot[0], yaw=rot[1]))
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label() == "ShotCam": unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(a)
