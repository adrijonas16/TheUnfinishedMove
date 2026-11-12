import unreal, importlib, traceback
import tum_art as A; importlib.reload(A)
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); V = unreal.Vector
MATP = "/Game/TUM/Materials/Surfaces"; DCS = "/Game/DerelictCorridor/Assets/Fab/Megascans/Surfaces"
GRIDS = ("MI_PrototypeGrid_Gray", "MI_PrototypeGrid_TopDark")
def master_orm():
    p = f"{MATP}/MAT_SurfaceWorldORM"
    if EAL.does_asset_exist(p): return EAL.load_asset(p)
    m = AT.create_asset("MAT_SurfaceWorldORM", MATP, unreal.Material, unreal.MaterialFactoryNew())
    fwt = EAL.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture")
    fwn = EAL.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal")
    size = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1200, 0); size.set_editor_property("parameter_name", "TileSize"); size.set_editor_property("default_value", 300.0)
    def tp(name, y, d, st):
        t = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -1200, y); t.set_editor_property("parameter_name", name)
        t.set_editor_property("texture", EAL.load_asset(d)); t.set_editor_property("sampler_type", st); return t
    def wa(fn, t, y):
        f = MEL.create_material_expression(m, unreal.MaterialExpressionMaterialFunctionCall, -800, y); f.set_material_function(fn)
        MEL.connect_material_expressions(t, "", f, "TextureObject"); MEL.connect_material_expressions(size, "", f, "TextureSize"); return f
    c = wa(fwt, tp("BaseColor", -400, "/Engine/EngineResources/DefaultTexture", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR), -400)
    n = wa(fwn, tp("Normal", 200, "/Engine/EngineMaterials/DefaultNormal", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL), 200)
    o = wa(fwt, tp("ORM", 600, "/Engine/EngineResources/WhiteSquareTexture", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR), 600)
    tint = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, -600); tint.set_editor_property("parameter_name", "Tint"); tint.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
    mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, -400); MEL.connect_material_expressions(c, "XYZ Texture", mul, "A"); MEL.connect_material_expressions(tint, "", mul, "B")
    def mask(ch, y):
        k = MEL.create_material_expression(m, unreal.MaterialExpressionComponentMask, -500, y)
        for c_ in "RGBA": k.set_editor_property(c_, c_ == ch)
        MEL.connect_material_expressions(o, "XYZ Texture", k, ""); return k
    rk, mk = mask("G", 600), mask("B", 800)
    rm = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -500, 700); rm.set_editor_property("parameter_name", "RoughnessMul"); rm.set_editor_property("default_value", 1.0)
    mm = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -500, 900); mm.set_editor_property("parameter_name", "MetallicMul"); mm.set_editor_property("default_value", 1.0)
    r = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 600); MEL.connect_material_expressions(rk, "", r, "A"); MEL.connect_material_expressions(rm, "", r, "B")
    me = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 800); MEL.connect_material_expressions(mk, "", me, "A"); MEL.connect_material_expressions(mm, "", me, "B")
    MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR); MEL.connect_material_property(n, "XYZ Texture", unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS); MEL.connect_material_property(me, "", unreal.MaterialProperty.MP_METALLIC)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def mi(name, folder, tile=300.0, rough=1.0, metal=1.0, tint=(1, 1, 1), noorm_rough=None):
    p = f"{MATP}/MI_W_{name}"
    x = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(f"MI_W_{name}", MATP, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(x, master_orm())
    for k, suf in (("BaseColor", "_B"), ("Normal", "_N"), ("ORM", "_ORM")):
        tp = f"{DCS}/{folder}/T_{folder}{suf}"
        if EAL.does_asset_exist(tp): MEL.set_material_instance_texture_parameter_value(x, k, EAL.load_asset(tp))
    MEL.set_material_instance_scalar_parameter_value(x, "TileSize", tile); MEL.set_material_instance_scalar_parameter_value(x, "RoughnessMul", rough)
    MEL.set_material_instance_scalar_parameter_value(x, "MetallicMul", metal); MEL.set_material_instance_vector_parameter_value(x, "Tint", unreal.LinearColor(*tint, 1))
    EAL.save_loaded_asset(x, False); return x
def fit(sub, box, folder, uniform=False, yaw=0.0):
    o, e = box.get_actor_bounds(False)
    return A.place(sub, o.x, o.y, o.z - e.z, size=(2 * e.x, 2 * e.y, 2 * e.z), uniform=uniform, yaw=yaw, folder=folder, collide=False)
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    out = {"err": {}}
    floor = mi("FloorDirty", "Ind_Unf_Floor_Concrete_Dirty_02", tile=400.0)
    metal = mi("MetalCorroded", "Ind_Sheet_Metal_Corroded_26", tile=250.0, rough=0.8, metal=0.0)
    wall = mi("WallPainted", "Ind_Wall_Concrete_Painted_08", tile=350.0, metal=0.0)
    for x in (metal,):
        MEL.set_material_instance_texture_parameter_value(x, "ORM", EAL.load_asset("/Engine/EngineResources/WhiteSquareTexture"))
        MEL.set_material_instance_scalar_parameter_value(x, "RoughnessMul", 0.65); MEL.set_material_instance_scalar_parameter_value(x, "MetallicMul", 0.6); EAL.save_loaded_asset(x, False)
    MEL.set_material_instance_texture_parameter_value(wall, "ORM", EAL.load_asset("/Engine/EngineResources/WhiteSquareTexture")); MEL.set_material_instance_scalar_parameter_value(wall, "RoughnessMul", 0.9); MEL.set_material_instance_scalar_parameter_value(wall, "MetallicMul", 0.0); EAL.save_loaded_asset(wall, False)
    A.LES().load_level("/Game/TUM/Maps/M_FactoryHub")
    for a in A.EAS().get_all_level_actors():
        if unreal.Name("ArtPass") in a.tags and str(a.get_folder_path()).startswith(("Art/Dress", "Art/City")): A.EAS().destroy_actor(a)
    n = {"floor": 0, "metal": 0, "wall": 0, "dressed": 0}
    for a in list(A.EAS().get_all_level_actors()):
        if not isinstance(a, unreal.StaticMeshActor) or unreal.Name("ArtPass") in a.tags: continue
        l = a.get_actor_label(); c = a.static_mesh_component
        if not c.is_visible(): continue
        cur = c.get_material(0); curn = cur.get_name() if cur else ""
        try:
            if l.startswith(("Loom_N", "Loom_S")):
                fit("SM_Ind_Container_Metal_Set_01_" + "ABCDE"[n["dressed"] % 5], a, "Art/Dress/Looms"); c.set_visibility(False); a.set_actor_hidden_in_game(True); n["dressed"] += 1
            elif l.startswith("Fabric_"):
                fit("SM_Ind_AbaFact_Tarp_Wrinkled_01", a, "Art/Dress/Tarps"); c.set_visibility(False); a.set_actor_hidden_in_game(True); n["dressed"] += 1
            elif l.startswith("Floor"): c.set_material(0, floor); n["floor"] += 1
            elif l.startswith(("Cell_", "FocusGate_Wall", "Wall_Start", "Wall_End", "NaveWall", "Ext_Passage")): c.set_material(0, wall); n["wall"] += 1
            elif curn in GRIDS or l.startswith(("Entry_", "Catwalk", "DragonStep", "WarBridge", "Cliff_Ledge", "Block_", "Crane", "Anchor_")): c.set_material(0, metal); n["metal"] += 1
        except Exception: out["err"][l] = traceback.format_exc()[-300:]
    out["n"] = n
    for a in A.EAS().get_all_level_actors():
        if isinstance(a, unreal.PlayerStart): a.set_actor_location(V(150, 0, 120), False, False); a.set_actor_rotation(unreal.Rotator(0, 0, 0), False)
        if a.get_actor_label() == "CP_Outside": A.EAS().destroy_actor(a)
    # city seen through the warehouse windows: photoscanned brick buildings around, night lights
    fm = EAL.load_asset("/Game/TUM/Environment/Facade/FBX_1_mln_2x16K_N")
    try:
        ns = fm.get_editor_property("nanite_settings"); ns.set_editor_property("enabled", True); fm.set_editor_property("nanite_settings", ns); EAL.save_loaded_asset(fm, False)
    except Exception: out["err"]["nanite"] = traceback.format_exc()[-300:]
    for i, (cx, cy, yaw) in enumerate(((800, 4200, -90), (6200, 4600, -90), (2600, -4400, 90), (8200, -4300, 90), (11200, 0, 180))):
        a = A.EAS().spawn_actor_from_object(fm, V(0, 0, 0), unreal.Rotator(0, 0, yaw)); o, e = a.get_actor_bounds(False)
        a.set_actor_location(V(cx - o.x, cy - o.y, -(o.z - e.z)), False, False); a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        a.set_actor_label(f"City_Facade_{i}"); a.set_folder_path("Art/City"); a.tags = [unreal.Name("ArtPass")]
    for i, (x, y) in enumerate(((800, 3500), (6200, 3900), (2600, -3700), (8200, -3600), (4000, 3800), (5200, -3800))):
        l = A.EAS().spawn_actor_from_class(unreal.PointLight, V(x, y, 900 + 300 * (i % 2)), unreal.Rotator(0, 0, 0))
        lc = l.get_component_by_class(unreal.LightComponent); lc.set_intensity(12000.0); lc.set_light_color(unreal.LinearColor(1.0, 0.7, 0.38, 1)); lc.set_editor_property("attenuation_radius", 2600.0)
        l.set_actor_label(f"City_Light_{i}"); l.set_folder_path("Art/City"); l.tags = [unreal.Name("ArtPass")]
    for a in A.EAS().get_all_level_actors():
        if isinstance(a, unreal.DirectionalLight):
            a.set_actor_rotation(unreal.Rotator(0, -32, -40), False); lc = a.get_component_by_class(unreal.LightComponent); lc.set_intensity(0.6); lc.set_light_color(unreal.LinearColor(0.55, 0.68, 1.0, 1))
        if isinstance(a, unreal.SkyLight): a.get_component_by_class(unreal.SkyLightComponent).set_intensity(0.5)
    A.LES().save_current_level()
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(V(300, -300, 250), unreal.Rotator(roll=0, pitch=-2, yaw=15))
    return out
