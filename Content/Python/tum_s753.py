# Factory materials, fixed for real: the old world/triplanar masters fail to compile for several instances (sampler-type and
# virtual-texture mismatches), so the engine showed its default checker. One small new master (world-aligned colour + normal,
# roughness/metallic as numbers, no packed texture) and seven instances that only use non-virtual textures.
import unreal, importlib, traceback
import tum_fac as K; importlib.reload(K)
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = K.E; L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); MS = K.MS
DCS = "/Game/DerelictCorridor/Assets/Fab/Megascans/Surfaces"
def master():
    p = f"{MS}/MAT_FacWorld"
    if EAL.does_asset_exist(p): return EAL.load_asset(p)
    m = AT.create_asset("MAT_FacWorld", MS, unreal.Material, unreal.MaterialFactoryNew())
    fwt = EAL.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture"); fwn = EAL.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal")
    def ex(cls, x, y, **kw):
        e = MEL.create_material_expression(m, cls, x, y)
        for k, v in kw.items(): e.set_editor_property(k, v)
        return e
    size = ex(unreal.MaterialExpressionScalarParameter, -1200, 0, parameter_name="TileSize", default_value=300.0)
    tc = ex(unreal.MaterialExpressionTextureObjectParameter, -1200, -400, parameter_name="BaseColor", texture=EAL.load_asset("/Engine/EngineResources/DefaultTexture"), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    tn = ex(unreal.MaterialExpressionTextureObjectParameter, -1200, 200, parameter_name="Normal", texture=EAL.load_asset("/Engine/EngineMaterials/DefaultNormal"), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    fc = ex(unreal.MaterialExpressionMaterialFunctionCall, -800, -400); fc.set_material_function(fwt); MEL.connect_material_expressions(tc, "", fc, "TextureObject"); MEL.connect_material_expressions(size, "", fc, "TextureSize")
    fn = ex(unreal.MaterialExpressionMaterialFunctionCall, -800, 200); fn.set_material_function(fwn); MEL.connect_material_expressions(tn, "", fn, "TextureObject"); MEL.connect_material_expressions(size, "", fn, "TextureSize")
    tint = ex(unreal.MaterialExpressionVectorParameter, -500, -600, parameter_name="Tint", default_value=unreal.LinearColor(1, 1, 1, 1))
    mul = ex(unreal.MaterialExpressionMultiply, -300, -400); MEL.connect_material_expressions(fc, "XYZ Texture", mul, "A"); MEL.connect_material_expressions(tint, "", mul, "B")
    r = ex(unreal.MaterialExpressionScalarParameter, -300, 300, parameter_name="Roughness", default_value=0.85); me = ex(unreal.MaterialExpressionScalarParameter, -300, 400, parameter_name="Metallic", default_value=0.0)
    MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR); MEL.connect_material_property(fn, "XYZ Texture", unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS); MEL.connect_material_property(me, "", unreal.MaterialProperty.MP_METALLIC)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def inst(name, color, normal, tile, rough, metal, tint):
    p = f"{MS}/{name}"
    x = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(name, MS, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(x, master()); c = EAL.load_asset(color); n = EAL.load_asset(normal)
    for t in (c, n):
        if t is None or bool(t.get_editor_property("virtual_texture_streaming")): raise RuntimeError(f"{name}: missing or virtual texture {color} / {normal}")
    MEL.set_material_instance_texture_parameter_value(x, "BaseColor", c); MEL.set_material_instance_texture_parameter_value(x, "Normal", n)
    for k, v in (("TileSize", tile), ("Roughness", rough), ("Metallic", metal)): MEL.set_material_instance_scalar_parameter_value(x, k, v)
    MEL.set_material_instance_vector_parameter_value(x, "Tint", unreal.LinearColor(tint[0], tint[1], tint[2], 1)); EAL.save_loaded_asset(x, False); return x
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_FactoryHub"); out = {}
    BR = "/Game/TUM/Textures/Surfaces/Bricks059/Bricks059_1K-JPG_"; MC = f"{DCS}/Ind_Sheet_Metal_Corroded_26/T_Ind_Sheet_Metal_Corroded_26"; FL = f"{DCS}/Ind_Unf_Floor_Concrete_Dirty_02/T_Ind_Unf_Floor_Concrete_Dirty_02"
    WP = f"{DCS}/Ind_Wall_Concrete_Painted_08/T_Ind_Wall_Concrete_Painted_08_B"; DN = "/Engine/EngineMaterials/DefaultNormal"
    M = {"brick": inst("MI_Fac_Brick", BR + "Color", BR + "NormalDX", 240.0, 0.9, 0.0, (0.8, 0.74, 0.7)),
         "conc": inst("MI_Fac_Concrete", WP, DN, 350.0, 0.9, 0.0, (0.62, 0.62, 0.62)),
         "steel": inst("MI_Fac_Steel", MC + "_B", MC + "_N", 220.0, 0.72, 0.65, (0.42, 0.42, 0.45)),
         "rust": inst("MI_Fac_Rust", MC + "_B", MC + "_N", 250.0, 0.68, 0.55, (0.9, 0.85, 0.8)),
         "rail": inst("MI_Fac_Rail", MC + "_B", MC + "_N", 160.0, 0.6, 0.55, (0.6, 0.52, 0.28)),
         "grate": inst("MI_Fac_Grate", MC + "_B", MC + "_N", 140.0, 0.6, 0.7, (0.4, 0.42, 0.45)),
         "roof": inst("MI_Fac_Roof", MC + "_B", MC + "_N", 320.0, 0.85, 0.3, (0.22, 0.22, 0.24)),
         "floor": inst("MI_Fac_Floor", FL + "_B", FL + "_N", 420.0, 0.34, 0.0, (0.62, 0.65, 0.68))}
    MAP = {"MI_W_SteelDark": "steel", "MI_W_RailPaint": "rail", "MI_W_Grate": "grate", "MI_W_RoofSheet": "roof", "MI_W_FloorWet": "floor", "MI_W_FloorDirty": "floor", "MI_W_MetalCorroded": "rust",
           "MI_W_FacBrick": "brick", "MI_Bricks059": "brick", "MI_W_WallOld": "brick", "MI_W_FacConcrete": "conc", "MI_W_WallPainted": "conc", "MI_W_WallDado": "conc", "MI_CorrugatedSteel005": "roof"}
    n = {}
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("TESTPANEL") or a.get_actor_label().startswith("TESTFLOOR"): E.destroy_actor(a); continue
        if not isinstance(a, unreal.StaticMeshActor): continue
        c = a.static_mesh_component; sm = c.static_mesh
        if not sm or sm.get_name() not in ("Cube", "Cylinder", "Plane"): continue
        m = c.get_material(0); nm = m.get_name() if m else ""
        if nm in MAP: c.set_material(0, M[MAP[nm]]); n[MAP[nm]] = n.get(MAP[nm], 0) + 1
    out["n"] = n; L.save_current_level(); return out
