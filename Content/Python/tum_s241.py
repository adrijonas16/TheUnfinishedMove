import unreal, json
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
def fog(mp, base_density, low_density, low_offset, color):
    L.load_level(mp); out = {}
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() == "VolClouds": E.destroy_actor(a); out["vc"] = "removed"
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.ExponentialHeightFog):
            c = a.component
            c.set_fog_density(base_density); c.set_editor_property("fog_height_falloff", 0.2)
            sd = c.get_editor_property("second_fog_data")
            sd.set_editor_property("fog_density", low_density); sd.set_editor_property("fog_height_falloff", 0.9); sd.set_editor_property("fog_height_offset", low_offset)
            c.set_editor_property("second_fog_data", sd)
            c.set_fog_inscattering_color(unreal.LinearColor(*color, 1)); out["fog"] = "ok"
    L.save_current_level(); return out
def run():
    return {"cliff": fog("/Game/TUM/Maps/M_Cut_Cliff", 0.02, 1.2, -1600.0, (0.55, 0.62, 0.72)),
            "dragon": fog("/Game/TUM/Maps/M_Cut_Dragon", 0.015, 1.5, -1000.0, (0.8, 0.72, 0.62))}
