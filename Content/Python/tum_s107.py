# Real Room v2: small modern bedroom (Poly Haven CC0 + FreeFurniturePack modern pieces + Meshy community headphones)
import unreal, importlib, os, json
import tum_lib as T; importlib.reload(T)
import tum_art as A; importlib.reload(A)
import tum_ph as PH; importlib.reload(PH)
import tum_s42 as S42; importlib.reload(S42)
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); V = unreal.Vector
MV = "/Game/TUM/Materials/Surfaces"
def ph_texture(tid, tint=(1, 1, 1), rough=1.0, tile=200.0):
    files = json.loads(PH._get(f"https://api.polyhaven.com/files/{tid}")); d = os.path.join(PH.ROOT, "tex_" + tid); os.makedirs(d, exist_ok=True); tx = {}
    for key, out in (("Diffuse", "Color"), ("nor_dx", "NormalDX"), ("Rough", "Roughness")):
        p = os.path.join(d, f"{tid}_{out}.jpg"); open(p, "wb").write(PH._get(files[key]["2k"]["jpg"]["url"]))
        t = S42.imp(p, f"/Game/TUM/Textures/Surfaces/{tid}")
        if out != "Color": t.set_editor_property("srgb", False)
        if out == "NormalDX": t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        if out == "Roughness": t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        EAL.save_loaded_asset(t, False); tx[out] = t
    return S42.instance(tid, S42.master(), tx, tint, rough, 0.0, tile)
def flat(name, color, metal, rough):
    p = f"{MV}/{name}"
    if EAL.does_asset_exist(p): return p
    m = AT.create_asset(name, MV, unreal.Material, unreal.MaterialFactoryNew())
    for i, (v, prop) in enumerate(((color, unreal.MaterialProperty.MP_BASE_COLOR), (metal, unreal.MaterialProperty.MP_METALLIC), (rough, unreal.MaterialProperty.MP_ROUGHNESS))):
        if isinstance(v, tuple): e = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, i * 150); e.set_editor_property("constant", unreal.LinearColor(*v, 1))
        else: e = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -400, i * 150); e.set_editor_property("r", v)
        MEL.connect_material_property(e, "", prop)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return p
def import_glb(path, dest):
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
    AT.import_asset_tasks([t]); return [p for p in t.imported_object_paths if isinstance(EAL.load_asset(p), unreal.StaticMesh)]
def assets():
    out = {"floor": ph_texture("laminate_floor_02", (0.9, 0.85, 0.8), 1.0, 220.0), "wall": ph_texture("white_plaster_02", (0.78, 0.8, 0.82), 1.0, 250.0)}
    out["alu"] = flat("M_BlackAluminum", (0.015, 0.015, 0.017), 0.9, 0.32); out["sill"] = flat("M_WhiteSill", (0.75, 0.75, 0.74), 0.0, 0.25)
    out["ph"] = PH.fetch_and_import(["side_table_01", "steel_frame_shelves_03", "modern_ceiling_lamp_01", "throw_pillows_01", "hanging_picture_frame_01", "hanging_picture_frame_03"])
    out["hp"] = import_glb(r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\meshy\Headphones.glb", "/Game/TUM/Props/Meshy/Headphones")
    return out
PHR = "/Game/TUM/Props/PolyHaven"
def ph(aid, x, y, z, yaw=0.0, scale=1.0, label=None, folder="Room/Furniture", collide=False, tags=()):
    meshes = [EAL.load_asset(p) for p in EAL.list_assets(f"{PHR}/{aid}", True, False) if isinstance(EAL.load_asset(p), unreal.StaticMesh)]
    mnz = min(m.get_bounding_box().min.z for m in meshes) * scale; out = []
    for i, m in enumerate(meshes):
        a = A.EAS().spawn_actor_from_object(m, V(x, y, z - mnz), unreal.Rotator(roll=0, pitch=0, yaw=yaw)); a.set_actor_scale3d(V(scale, scale, scale))
        if not collide: a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        a.set_actor_label((label or aid) + (f"_{i}" if i else "")); a.set_folder_path(folder); a.tags = [unreal.Name("ArtPass")] + [unreal.Name(t) for t in tags]; out.append(a)
    return out
def top_of(a): o, e = a.get_actor_bounds(False); return o.z + e.z
def room():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    A.LES().load_level("/Game/TUM/Maps/M_RealRoom")
    keep = ("RealRoomRoute", "Ending_Text_0", "Ending_Text_1", "Ending_Text_2")
    for a in A.EAS().get_all_level_actors():
        if a.get_actor_label() in keep or isinstance(a, (unreal.PostProcessVolume, unreal.SkyLight, unreal.ExponentialHeightFog, unreal.SkyAtmosphere, unreal.WorldSettings)): continue
        if unreal.Name("TUM_Built") in a.tags or unreal.Name("ArtPass") in a.tags or isinstance(a, unreal.PlayerStart): A.EAS().destroy_actor(a)
    R = "Room"; wall = f"{MV}/MI_white_plaster_02"; floor = f"{MV}/MI_laminate_floor_02"; alu = f"{MV}/M_BlackAluminum"; sill = f"{MV}/M_WhiteSill"
    def b(l, *a, **k): return T.box(l, *a, folder=R, **k)
    b("Room_Floor", -280, 280, -240, 240, -20, 0, floor); b("Room_Ceiling", -280, 280, -240, 240, 270, 285, wall)
    b("Room_Wall_W", -295, -280, -240, 240, 0, 270, wall); b("Room_Wall_E", 280, 295, -240, 240, 0, 270, wall); b("Room_Wall_S", -280, 280, -255, -240, 0, 270, wall)
    b("Room_Wall_N_L", -280, -160, 240, 255, 0, 270, wall); b("Room_Wall_N_R", 160, 280, 240, 255, 0, 270, wall)
    b("Room_Wall_N_Low", -160, 160, 240, 255, 0, 75, wall); b("Room_Wall_N_Top", -160, 160, 240, 255, 245, 270, wall)
    b("Baseboard_W", -281, -279, -240, 240, 0, 8, sill, collide=False); b("Baseboard_E", 279, 281, -240, 240, 0, 8, sill, collide=False); b("Baseboard_S", -280, 280, -241, -239, 0, 8, sill, collide=False)
    # modern window: slim black aluminium frame, one mullion, white stone sill
    W = "Room/Window"
    for l, x0, x1, z0, z1 in (("L", -160, -154, 75, 245), ("R", 154, 160, 75, 245), ("B", -160, 160, 75, 81), ("T", -160, 160, 239, 245), ("M", -3, 3, 81, 239)):
        T.box(f"Window_Frame_{l}", x0, x1, 241, 251, z0, z1, alu, W, collide=False)
    T.box("Window_Sill", -172, 172, 222, 246, 71, 75, sill, W, collide=False)
    T.box("Window_Glass", -154, 154, 247, 248, 81, 239, f"{MV}/MAT_DirtyGlass", W, collide=True)
    F = "Room/Furniture"
    desk = A.place("SM_Modern_Table", 0, 185, 0, size=(150, 70, 75), uniform=False, collide=True, folder=F, label="Desk"); top = top_of(desk)
    A.place("SM_Modern_Office_chair", 5, 105, 0, size=(None, None, 105), yaw=180, collide=True, folder=F, label="Desk_Chair")
    A.place("SM_Modern_Bed_2", -195, -135, 0, size=(165, 215, None), collide=True, folder=F, label="Bed")
    ph("throw_pillows_01", -200, -205, 48, yaw=0, label="Pillows")
    st = ph("side_table_01", -85, -215, 0, label="Side_Table")[0]
    A.place("SM_Bed_lamp_3", -85, -215, top_of(st), size=(None, None, 45), folder=F, label="Bed_Lamp")
    A.place("SM_Modern_Cupboard", 250, -140, 0, size=(None, None, 220), yaw=-90, collide=True, folder=F, label="Wardrobe")
    sh = ph("steel_frame_shelves_03", 255, 100, 0, yaw=90, label="Shelves", collide=True)
    ph("book_encyclopedia_set_01", 255, 95, 120, yaw=-90, label="Books")
    ph("potted_plant_04", 225, 205, 0, label="Plant")
    ph("hanging_picture_frame_01", -278, -120, 150, yaw=90, label="Frame_A"); ph("hanging_picture_frame_03", -278, -40, 165, yaw=90, label="Frame_B")
    lamp = ph("modern_ceiling_lamp_01", 0, 0, 0, label="Ceiling_Lamp")
    for a in lamp: a.set_actor_location(V(0, 0, 270 - (top_of(lamp[0]) - a.get_actor_location().z)), False, False)
    ph("desk_lamp_arm_01", -55, 205, top, yaw=200, label="Desk_Lamp")
    ph("standing_picture_frame_02", 60, 215, top, yaw=190, label="Desk_Photo")
    A.place("KnightWhite", 40, 190, top, size=(None, None, 16), yaw=200, folder=F, label="Knight_Desk_Mesh", tags=("Ending",)).set_actor_hidden_in_game(True)
    A.place("KnightWhite", 40, 190, top, size=(None, None, 16), yaw=200, folder=F, label="Knight_Desk_Intro", tags=("Intro",))
    A.place("Headphones", -5, 165, top, size=(22, None, None), yaw=160, folder=F, label="Headphones", tags=("Intro",))
    hint = T.text("Hint_Headphones", 0, 160, top + 30, "put on the headphones", 6.0, (1.0, 0.85, 0.6), -90.0, R); hint.tags = list(hint.tags) + [unreal.Name("Intro")]
    t = A.EAS().spawn_actor_from_class(EAL.load_asset("/Game/TUM/Core/BP_Trigger").generated_class(), V(0, 150, 100), unreal.Rotator(0, 0, 0))
    for k, v in (("Radius", 100.0), ("bOpenMap", True), ("TargetMap", "M_FactoryHub"), ("Flag", 0)): t.set_editor_property(k, v)
    T.tag(t, "Trigger_Headphones", "Gameplay", ("Intro", "CutAnchor_Factory"))
    T.light("Lamp_Light", -55, 195, top + 40, (1.0, 0.68, 0.38), 900.0, 500.0, "Room/Lights")
    T.light("Bed_Light", -85, -215, 90, (1.0, 0.6, 0.35), 400.0, 350.0, "Room/Lights")
    T.light("Window_Light", 0, 600, 220, (0.5, 0.62, 0.95), 2500.0, 900.0, "Room/Lights", cls=unreal.SpotLight, rot=unreal.Rotator(roll=0, pitch=-20, yaw=-90))
    T.light("Room_Fill", 0, -60, 240, (0.6, 0.62, 0.75), 80.0, 500.0, "Room/Lights")
    import tum_s105; importlib.reload(tum_s105); tum_s105.place_dome(EAL.load_asset(f"{MV}/MAT_CityBackdrop"), V(0, 0, 0), 6000.0, 0.0)
    ps = A.EAS().spawn_actor_from_class(unreal.PlayerStart, V(170, -170, 120), unreal.Rotator(0, 0, 120)); ps.set_actor_label("PlayerStart"); ps.set_folder_path("Markers")
    for a in A.EAS().get_all_level_actors():
        if a.get_actor_label().startswith("Ending_Text"): a.set_actor_location(V(-200, 236, a.get_actor_location().z), False, False); a.set_actor_rotation(unreal.Rotator(0, 0, -90), False)
    A.LES().save_current_level()
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(V(200, -200, 165), unreal.Rotator(roll=0, pitch=-10, yaw=125))
    return "ok"
