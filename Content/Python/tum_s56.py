import unreal, importlib
import tum_art as A; importlib.reload(A)
def sun(pitch, inten):
    for a in A.EAS().get_all_level_actors():
        if isinstance(a, unreal.DirectionalLight):
            a.set_actor_rotation(unreal.Rotator(roll=0, pitch=pitch, yaw=-35), False); a.get_component_by_class(unreal.LightComponent).set_intensity(inten)
def drop(folder_sub):
    n = 0
    for a in A.EAS().get_all_level_actors():
        if unreal.Name("ArtPass") in a.tags and folder_sub in str(a.get_folder_path()): A.EAS().destroy_actor(a); n += 1
    return n
def run():
    out = {}
    A.LES().load_level("/Game/TUM/Maps/M_Cut_WarField")
    out["war_drop"] = drop("Horizon")
    for i, (x, y) in enumerate(((9000, -3500), (9500, 500), (9000, 3800), (3000, -6500), (3000, 6500))):
        A.place("Modular_ChurchRuin_Stone_Kit", x, y, 0, size=(None, None, 1600), yaw=90 + i * 40, folder="Art/War/Horizon")
    sun(-42.0, 3.5); A.LES().save_current_level()
    A.LES().load_level("/Game/TUM/Maps/M_Cut_Cliff")
    out["cliff_drop"] = drop("Pillars")
    for i, (x, y, h) in enumerate(((1500, -5200, 3600), (3500, -5600, 4200), (5600, -5000, 3400), (2000, 5200, 3800), (4200, 5600, 4400), (9500, 0, 4600))):
        A.place("Massive_Nordic_Coastal_Cliff", x, y, -2300, size=(None, None, h), yaw=i * 61, folder="Art/Cliff/Pillars")
    sun(-38.0, 4.0); A.LES().save_current_level()
    A.LES().load_level("/Game/TUM/Maps/M_FactoryHub"); return out
