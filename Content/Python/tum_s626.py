# Knights: every soldier clip faces mesh +Y, so the body is always turned -90 (no more running backwards). Keeps the sword-reach strike.
import unreal, importlib
import tum_s617 as K; importlib.reload(K)
def run():
    K.K566.turn = lambda mod_g, var, anim: f"(Transformation|SetActorRelativeRotation :self {mod_g(var)} :NewRelativeRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw -90.0))"
    r = K.run()
    E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    L.load_level("/Game/TUM/Maps/M_Cut_WarField"); n = 0
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith("Knight_") and not isinstance(a, (unreal.SkeletalMeshActor, unreal.StaticMeshActor)):
            b = a.get_editor_property("Body")
            if b: b.root_component.set_relative_rotation(unreal.Rotator(roll=0, pitch=0, yaw=-90), False, False); n += 1
    L.save_current_level(); r["bodies"] = n; return r
