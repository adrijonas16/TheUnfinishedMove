# Factory look fix: puddles get real material, gameplay fabric boxes hidden in game, real 3D city around the warehouse windows, exposure
import unreal, importlib
import tum_s129 as C; importlib.reload(C)
import tum_s77 as P; importlib.reload(P)
EAL = unreal.EditorAssetLibrary; V = unreal.Vector
def E(): return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def run():
    pud = EAL.load_asset("/Game/Materials/Custom/MI_MS_Puddle")
    out = {"puddles": 0}
    for a in E().get_all_level_actors():
        l = a.get_actor_label()
        if l.startswith("Art_SM_Water") and isinstance(a, unreal.StaticMeshActor):
            for i in range(a.static_mesh_component.get_num_materials()): a.static_mesh_component.set_material(i, pud)
            out["puddles"] += 1
        if l.startswith("Fabric_") and isinstance(a, unreal.StaticMeshActor): a.set_actor_hidden_in_game(True)
        if l.startswith("City_Facade_"): E().destroy_actor(a)
    out["city"] = C.place_multi([((3600, 42000, -6500), 0.0), ((3600, -42000, -6500), 180.0), ((48000, 0, -6500), 90.0)])
    out["mats"] = C.unlit(3.0)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return out
