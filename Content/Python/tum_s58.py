import unreal, importlib
import tum_art as A; importlib.reload(A)
def drop(pred):
    n = 0
    for a in A.EAS().get_all_level_actors():
        if unreal.Name("ArtPass") in a.tags and pred(a): A.EAS().destroy_actor(a); n += 1
    return n
def unhide(subs):
    for a in A.EAS().get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor) and unreal.Name("ArtPass") not in a.tags and any(s in a.get_actor_label() for s in subs):
            a.set_actor_hidden_in_game(False); a.static_mesh_component.set_visibility(True)
def sky(i):
    for a in A.EAS().get_all_level_actors():
        if isinstance(a, unreal.SkyLight): a.get_component_by_class(unreal.SkyLightComponent).set_intensity(i)
def run():
    out = {}
    A.LES().load_level("/Game/TUM/Maps/M_Cut_WarField")
    out["war"] = drop(lambda a: "Horizon" in str(a.get_folder_path())); sky(1.6); A.LES().save_current_level()
    A.LES().load_level("/Game/TUM/Maps/M_Cut_Cliff")
    out["cliff"] = drop(lambda a: str(a.get_folder_path()) == "Art/Cliff"); unhide(["Start_Ledge", "End_Ledge", "Start_CliffWall", "Arch_Pillar", "Arch_Lintel"]); sky(1.6)
    A.LES().save_current_level(); A.LES().load_level("/Game/TUM/Maps/M_FactoryHub"); return out
