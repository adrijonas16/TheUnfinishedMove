import unreal, os
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
def shots(mp, views, w=1280, h=720):
    LES.load_level(f"/Game/TUM/Maps/{mp}")
    out = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), "ClaudeShots")
    world = unreal.EditorLevelLibrary.get_editor_world()
    rt = unreal.RenderingLibrary.create_render_target2d(world, w, h, unreal.TextureRenderTargetFormat.RTF_RGBA8_SRGB)
    for n, (loc, rot, fov) in views.items():
        cap = EAS.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(*loc), unreal.Rotator(roll=0, pitch=rot[0], yaw=rot[1]))
        c = cap.capture_component2d; c.set_editor_property("texture_target", rt); c.set_editor_property("fov_angle", fov)
        c.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR); c.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, rt, out, n + ".png"); EAS.destroy_actor(cap)
    return list(views)
