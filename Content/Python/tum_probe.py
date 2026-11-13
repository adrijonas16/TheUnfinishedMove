import unreal, importlib, tum_anim as TA
importlib.reload(TA)
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary
def probe(name, keys, label="AnimProbe", loc=(0, -6000, 0), yaw=0):
    seq = TA.make(name, keys, 1.0)
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() == label: E.destroy_actor(a)
    a = E.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(*loc), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    c = a.skeletal_mesh_component
    c.set_skeletal_mesh_asset(EAL.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"))
    c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    d = unreal.SingleAnimationPlayData(); d.set_editor_property("anim_to_play", seq); d.set_editor_property("saved_position", 0.99)
    c.set_editor_property("animation_data", d); c.set_position(0.99, False)
    a.set_actor_label(label)
    return a
