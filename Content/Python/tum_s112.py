import unreal, importlib
import tum_s107
from tum_s107 import *
import tum_s108
def room2():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    A.LES().load_level("/Game/TUM/Maps/M_RealRoom")
    keep = ("RealRoomRoute", "Ending_Text_0", "Ending_Text_1", "Ending_Text_2")
    for a in A.EAS().get_all_level_actors():
        if a.get_actor_label() in keep or isinstance(a, (unreal.PostProcessVolume, unreal.SkyLight, unreal.ExponentialHeightFog, unreal.SkyAtmosphere, unreal.WorldSettings)): continue
        if unreal.Name("TUM_Built") in a.tags or unreal.Name("ArtPass") in a.tags or isinstance(a, unreal.PlayerStart): A.EAS().destroy_actor(a)
    R = "Room"; wall = f"{MV}/MI_white_plaster_02"; floor = f"{MV}/MI_laminate_floor_02"; alu = f"{MV}/M_BlackAluminum"; sill = f"{MV}/M_WhiteSill"
    def b(l, *a, **k): return T.box(l, *a, folder=R, **k)
    b("Room_Floor", -340, 340, -300, 300, -20, 0, floor); b("Room_Ceiling", -340, 340, -300, 300, 280, 295, wall)
    b("Room_Wall_W", -355, -340, -300, 300, 0, 280, wall); b("Room_Wall_E", 340, 355, -300, 300, 0, 280, wall); b("Room_Wall_S", -340, 340, -315, -300, 0, 280, wall)
    b("Room_Wall_N_L", -340, -160, 300, 315, 0, 280, wall); b("Room_Wall_N_R", 160, 340, 300, 315, 0, 280, wall)
    b("Room_Wall_N_Low", -160, 160, 300, 315, 0, 75, wall); b("Room_Wall_N_Top", -160, 160, 300, 315, 245, 280, wall)
    b("Baseboard_W", -341, -339, -300, 300, 0, 8, sill, collide=False); b("Baseboard_E", 339, 341, -300, 300, 0, 8, sill, collide=False); b("Baseboard_S", -340, 340, -301, -299, 0, 8, sill, collide=False)
    # modern window: slim black aluminium frame, one mullion, white stone sill
    W = "Room/Window"
    for l, x0, x1, z0, z1 in (("L", -160, -154, 75, 245), ("R", 154, 160, 75, 245), ("B", -160, 160, 75, 81), ("T", -160, 160, 239, 245), ("M", -3, 3, 81, 239)):
        T.box(f"Window_Frame_{l}", x0, x1, 301, 311, z0, z1, alu, W, collide=False)
    T.box("Window_Sill", -172, 172, 282, 306, 71, 75, sill, W, collide=False)
    T.box("Window_Glass", -154, 154, 307, 308, 81, 239, f"{MV}/MAT_DirtyGlass", W, collide=True)
    F = "Room/Furniture"
    desk = A.place("SM_Modern_Table", 0, 250, 0, scale=1.0, collide=True, folder=F, label="Desk"); top = top_of(desk)
    A.place("SM_Modern_Office_chair", 5, 175, 0, scale=1.0, yaw=180, collide=True, folder=F, label="Desk_Chair")
    A.place("SM_Modern_Bed_2", -222, -182, 0, scale=1.0, collide=True, folder=F, label="Bed")
    ph("throw_pillows_01", -222, -270, 62, yaw=0, label="Pillows")
    st = ph("side_table_01", -75, -270, 0, label="Side_Table")[0]
    A.place("SM_Bed_lamp_3", -75, -270, top_of(st), size=(None, None, 50), folder=F, label="Bed_Lamp")
    A.place("SM_Modern_Cupboard", 300, -160, 0, size=(None, None, 240), yaw=-90, collide=True, folder=F, label="Wardrobe")
    sh = ph("steel_frame_shelves_03", 312, 130, 0, yaw=90, label="Shelves", collide=True)
    ph("book_encyclopedia_set_01", 312, 125, 120, yaw=-90, label="Books")
    ph("potted_plant_04", 290, 270, 0, label="Plant")
    ph("hanging_picture_frame_01", -338, -10, 150, yaw=90, label="Frame_A"); ph("hanging_picture_frame_03", -338, 80, 165, yaw=90, label="Frame_B")
    lamp = ph("modern_ceiling_lamp_01", 0, 0, 0, label="Ceiling_Lamp")
    for a in lamp: a.set_actor_location(V(0, 0, 280 - (top_of(lamp[0]) - a.get_actor_location().z)), False, False)
    ph("desk_lamp_arm_01", -70, 270, top, yaw=200, scale=0.7, label="Desk_Lamp")
    ph("standing_picture_frame_02", 70, 275, top, yaw=190, label="Desk_Photo")
    A.place("KnightWhite", 45, 250, top, size=(None, None, 16), yaw=200, folder=F, label="Knight_Desk_Mesh", tags=("Ending",)).set_actor_hidden_in_game(True)
    A.place("KnightWhite", 45, 250, top, size=(None, None, 16), yaw=200, folder=F, label="Knight_Desk_Intro", tags=("Intro",))
    A.place("Headphones", -5, 225, top, size=(22, None, None), yaw=160, folder=F, label="Headphones", tags=("Intro",))
    hint = T.text("Hint_Headphones", 0, 215, top + 32, "put on the headphones", 6.0, (1.0, 0.85, 0.6), -90.0, R); hint.tags = list(hint.tags) + [unreal.Name("Intro")]
    t = A.EAS().spawn_actor_from_class(EAL.load_asset("/Game/TUM/Core/BP_Trigger").generated_class(), V(0, 200, 100), unreal.Rotator(0, 0, 0))
    for k, v in (("Radius", 110.0), ("bOpenMap", True), ("TargetMap", "M_FactoryHub"), ("Flag", 0)): t.set_editor_property(k, v)
    T.tag(t, "Trigger_Headphones", "Gameplay", ("Intro", "CutAnchor_Factory"))
    T.light("Lamp_Light", -60, 255, top + 40, (1.0, 0.68, 0.38), 250.0, 500.0, "Room/Lights")
    T.light("Bed_Light", -75, -270, 100, (1.0, 0.6, 0.35), 400.0, 350.0, "Room/Lights")
    T.light("Window_Light", 0, 600, 220, (0.5, 0.62, 0.95), 2500.0, 900.0, "Room/Lights", cls=unreal.SpotLight, rot=unreal.Rotator(roll=0, pitch=-20, yaw=-90))
    T.light("Room_Fill", 0, -60, 240, (0.6, 0.62, 0.75), 80.0, 500.0, "Room/Lights")
    import tum_s105; importlib.reload(tum_s105); tum_s105.place_dome(EAL.load_asset(f"{MV}/MAT_CityBackdrop"), V(0, 0, 0), 6000.0, 0.0)
    ps = A.EAS().spawn_actor_from_class(unreal.PlayerStart, V(90, -130, 100), unreal.Rotator(0, 0, 105)); ps.set_actor_label("PlayerStart"); ps.tags = [unreal.Name("RoomStart")]; ps.set_folder_path("Markers")
    for a in A.EAS().get_all_level_actors():
        if a.get_actor_label().startswith("Ending_Text"): a.set_actor_location(V(-250, 296, a.get_actor_location().z), False, False); a.set_actor_rotation(unreal.Rotator(0, 0, -90), False)
    A.LES().save_current_level()
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(V(90, -130, 165), unreal.Rotator(roll=0, pitch=-8, yaw=105))
    return "ok"

def finish():
    import tum_s108 as S8; importlib.reload(S8)
    S8.walls(); S8.fixes()
    for a in A.EAS().get_all_level_actors():
        if a.get_actor_label() == "City_Dome": a.set_actor_location(V(0, 0, -900), False, False)
        if a.get_actor_label() == "Lamp_Light": a.get_component_by_class(unreal.LightComponent).set_intensity(250.0)
    A.LES().save_current_level()
