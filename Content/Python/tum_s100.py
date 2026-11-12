import unreal, importlib, math
import tum_lib as T; importlib.reload(T)
import tum_art as A; importlib.reload(A)
EAL = unreal.EditorAssetLibrary; V = unreal.Vector
MV = "/Game/TUM/Materials/Surfaces"
def kill(pred):
    for a in A.EAS().get_all_level_actors():
        if pred(a): A.EAS().destroy_actor(a)
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    A.LES().load_level("/Game/TUM/Maps/M_RealRoom")
    keep = ("RealRoomRoute", "Ending_Text_0", "Ending_Text_1", "Ending_Text_2", "PP_Global", "SkyLight", "Fog", "SkyAtmosphere")
    kill(lambda a: a.get_actor_label() not in keep and not isinstance(a, (unreal.PostProcessVolume, unreal.SkyLight, unreal.ExponentialHeightFog, unreal.SkyAtmosphere, unreal.WorldSettings)) and (unreal.Name("TUM_Built") in a.tags or unreal.Name("ArtPass") in a.tags or isinstance(a, unreal.PlayerStart)))
    R = "Room"; plaster = f"{MV}/MI_W_WallPainted"; floor = f"{MV}/MI_W_FloorDirty"
    def b(l, *a, **k): return T.box(l, *a, folder=R, **k)
    b("Room_Floor", -420, 420, -420, 420, -20, 0, floor); b("Room_Ceiling", -420, 420, -420, 420, 300, 320, plaster)
    b("Room_Wall_W", -440, -420, -420, 420, 0, 300, plaster); b("Room_Wall_E", 420, 440, -420, 420, 0, 300, plaster); b("Room_Wall_S", -420, 420, -440, -420, 0, 300, plaster)
    # north wall with a big window over the desk (looks onto the rainy city)
    b("Room_Wall_N_L", -420, -240, 420, 440, 0, 300, plaster); b("Room_Wall_N_R", 240, 420, 420, 440, 0, 300, plaster)
    b("Room_Wall_N_Low", -240, 240, 420, 440, 0, 85, plaster); b("Room_Wall_N_Top", -240, 240, 420, 440, 270, 300, plaster)
    for i, x in enumerate((-240, -82, 78, 236)): b(f"Window_Frame_V{i}", x - 4, x + 4, 424, 436, 85, 270, "/Game/TUM/Materials/Surfaces/MI_Asphalt031")
    b("Window_Frame_Mid", -240, 240, 424, 436, 176, 182, "/Game/TUM/Materials/Surfaces/MI_Asphalt031")
    g = b("Window_Glass", -240, 240, 429, 431, 85, 270, "/Game/TUM/Materials/Surfaces/MAT_DirtyGlass", collide=True)
    F = "Room/Furniture"
    desk = A.place("SM_Old_Table", 0, 330, 0, size=(150, 75, None), yaw=0, collide=True, folder=F, label="Desk")
    A.place("SM_Modern_Office_chair", 10, 210, 0, size=(None, None, 105), yaw=180, collide=True, folder=F, label="Desk_Chair")
    A.place("SM_Modern_Bed_1", -270, -170, 0, size=(170, 220, None), yaw=0, collide=True, folder=F, label="Bed")
    A.place("SM_Bed_Table", -380, 90, 0, size=(None, None, 55), yaw=90, collide=True, folder=F, label="Bed_Table")
    A.place("SM_Bed_Lamp_1", -380, 90, 55, size=(None, None, 45), folder=F, label="Bed_Lamp")
    A.place("SM_WoodenShelf_02", 400, 150, 0, size=(None, None, 190), yaw=-90, collide=True, folder=F, label="Shelf")
    A.place("SM_VintageRadio", 395, 150, 110, size=(40, None, None), yaw=-90, folder=F, label="Radio")
    A.place("SM_Carpet_01", -60, -40, 0.5, size=(260, 180, None), uniform=False, folder=F, label="Carpet")
    A.place("SM_Commode", 380, -280, 0, size=(None, None, 85), yaw=-90, collide=True, folder=F, label="Commode")
    for i, (y, z) in enumerate(((-120, 170), (-40, 190), (30, 165))): A.place("SM_Picture", 417, y, z, size=(None, 40, None), yaw=-90, base=False, folder=F, label=f"Photo_{i}")
    dz = desk.get_actor_bounds(False); top = dz[0].z + dz[1].z
    # props on the desk (Meshy items replace these when ready)
    kn = [a for a in A.EAS().get_all_level_actors()]
    A.place("KnightWhite", 55, 300, top, size=(None, None, 16), yaw=200, folder=F, label="Knight_Desk_Mesh", tags=("Ending",)).set_actor_hidden_in_game(True)
    A.place("KnightWhite", 55, 300, top, size=(None, None, 16), yaw=200, folder=F, label="Knight_Desk_Intro", tags=("Intro",))
    hp = A.place("SM_Bed_Lamp_2", -50, 320, top, size=(None, None, 40), folder=F, label="Desk_Lamp")
    l = T.light("Lamp_Light", -50, 320, top + 35, (1.0, 0.68, 0.38), 1600.0, 700.0, "Room/Lights")
    T.light("Window_Light", 0, 600, 200, (0.55, 0.65, 0.9), 2500.0, 900.0, "Room/Lights", cls=unreal.SpotLight, rot=unreal.Rotator(roll=0, pitch=-20, yaw=-90))
    T.light("Room_Fill", 0, -100, 260, (0.6, 0.62, 0.75), 120.0, 700.0, "Room/Lights")
    # headphones placeholder (Meshy model swapped in later); walking up to them starts the night
    hb = T.box("Headphones", 10, 40, 300, 330, top, top + 10, "/Game/TUM/Materials/Surfaces/MI_Asphalt031", R, ("Intro",), collide=False)
    hint = T.text("Hint_Headphones", 25, 300, top + 28, "put on the headphones", 7.0, (1.0, 0.85, 0.6), -90.0, "Room"); hint.tags = list(hint.tags) + [unreal.Name("Intro")]
    t = A.EAS().spawn_actor_from_class(EAL.load_asset("/Game/TUM/Core/BP_Trigger").generated_class(), V(25, 290, 100), unreal.Rotator(0, 0, 0))
    for k, v in (("Radius", 110.0), ("bOpenMap", True), ("TargetMap", "M_FactoryHub"), ("Flag", 0)): t.set_editor_property(k, v)
    T.tag(t, "Trigger_Headphones", "Gameplay", ("Intro", "CutAnchor_Factory"))
    # city outside the window
    fm = EAL.load_asset("/Game/TUM/Environment/Facade/FBX_1_mln_2x16K_N")
    for i, (cx, cy, yaw) in enumerate(((-1500, 3600, -90), (2600, 4200, -90), (500, 7000, -90))):
        a = A.EAS().spawn_actor_from_object(fm, V(0, 0, 0), unreal.Rotator(0, 0, yaw)); o, e = a.get_actor_bounds(False)
        a.set_actor_location(V(cx - o.x, cy - o.y, -1500 - (o.z - e.z)), False, False); a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        a.set_actor_label(f"City_{i}"); a.set_folder_path("Room/City"); a.tags = [unreal.Name("ArtPass")]
    for i, (x, y, z) in enumerate(((-1200, 3300, 300), (2300, 3900, 600), (400, 6600, 900))):
        T.light(f"City_Light_{i}", x, y, z, (1.0, 0.7, 0.4), 30000.0, 2500.0, "Room/City")
    ps = A.EAS().spawn_actor_from_class(unreal.PlayerStart, V(250, -250, 120), unreal.Rotator(0, 0, 113)); ps.set_actor_label("PlayerStart"); ps.set_folder_path("Markers")
    for a in A.EAS().get_all_level_actors():
        if a.get_actor_label().startswith("Ending_Text"): a.set_actor_location(V(-150, 410, a.get_actor_location().z), False, False); a.set_actor_rotation(unreal.Rotator(0, 0, -90), False)
    A.LES().save_current_level()
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(V(250, -250, 165), unreal.Rotator(roll=0, pitch=-8, yaw=113))
    return "ok"
