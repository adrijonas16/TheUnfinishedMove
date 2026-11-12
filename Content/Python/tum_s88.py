import unreal, importlib, random
import tum_art as A; importlib.reload(A)
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    A.LES().load_level("/Game/TUM/Maps/M_FactoryHub")
    for a in A.EAS().get_all_level_actors():
        if unreal.Name("ArtPass") in a.tags and str(a.get_folder_path()).startswith("Art/Exterior/"): A.EAS().destroy_actor(a)
    F = "Art/Exterior/Nature"
    A.scatter(["SM_rbdoo_VarA", "SM_rbdoo_VarB", "SM_rbdoo_VarC"], 70, -6800, -1300, -4800, 4800, seed=11, smin=0.8, smax=1.5, folder=F)
    A.scatter(["SM_rbdoo_VarA", "SM_rbdoo_VarC"], 30, -1300, -400, -4000, 4000, seed=12, smin=0.6, smax=1.0, folder=F)
    for i, (x, y, yaw) in enumerate(((-6200, -3800, 20), (-5600, 3600, 140), (-3300, -4300, 260), (-2600, 4200, 80))):
        A.place("qlEtl_tier_0" if i % 2 else "qjovi_tier_0", x, y, 0, size=(None, None, 900), yaw=yaw, folder=F)
    A.place("vdcoefeva_tier_1", -4600, -2600, 0, size=(None, None, 250), yaw=40, folder=F)
    A.scatter(["SM_Ind_Rubble_Pile_Concrete_M_01", "SM_Ind_Rubble_Debris_Concrete_Pack_01_B", "SM_Ind_Ware_Storage_Pallet_Wood_Worn_01", "SM_Ind_Container_Oil_Plastic_Pack_01_A"], 14, -6500, -1500, -4500, 4500, seed=13, folder=F)
    A.LES().save_current_level()
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-6000, -300, 300), unreal.Rotator(roll=0, pitch=0, yaw=0))
    return "ok"
