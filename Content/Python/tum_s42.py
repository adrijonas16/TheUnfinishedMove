# Surface materials from CC0 ambientCG textures (pre-jam local download, declared in ledger)
import unreal, os
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary
SRC = r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\ambientcg"; TEX = "/Game/TUM/Textures/Surfaces"; MAT = "/Game/TUM/Materials/Surfaces"
SETS = ["Concrete034", "Concrete044A", "CorrugatedSteel005", "Ground037", "Ground080", "Grass004", "Rock030", "Rock035", "PaintedPlaster017", "Bricks059", "Asphalt031"]
def imp(path, dest):
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
    AT.import_asset_tasks([t]); return EAL.load_asset(t.imported_object_paths[0]) if t.imported_object_paths else None
def textures(name):
    d = os.path.join(SRC, name); out = {}
    for f in os.listdir(d):
        for key in ("Color", "NormalDX", "Roughness"):
            if f.endswith(f"_{key}.jpg"):
                tx = imp(os.path.join(d, f), f"{TEX}/{name}")
                if key == "NormalDX": tx.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP); tx.set_editor_property("srgb", False)
                if key == "Roughness": tx.set_editor_property("srgb", False); tx.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
                EAL.save_loaded_asset(tx, False); out[key] = tx
    return out
def master():
    p = f"{MAT}/MAT_SurfaceWorld"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("MAT_SurfaceWorld", MAT, unreal.Material, unreal.MaterialFactoryNew())
    fwt = EAL.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture")
    fwn = EAL.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal")
    size = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1200, 0); size.set_editor_property("parameter_name", "TileSize"); size.set_editor_property("default_value", 300.0)
    def tex_param(name, y, default_path, sampler):
        t = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -1200, y); t.set_editor_property("parameter_name", name)
        t.set_editor_property("texture", EAL.load_asset(default_path)); t.set_editor_property("sampler_type", sampler); return t
    def wat(fn, tobj, y):
        f = MEL.create_material_expression(m, unreal.MaterialExpressionMaterialFunctionCall, -800, y); f.set_material_function(fn)
        MEL.connect_material_expressions(tobj, "", f, "TextureObject"); MEL.connect_material_expressions(size, "", f, "TextureSize"); return f
    c = tex_param("BaseColor", -400, "/Engine/EngineResources/DefaultTexture", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    n = tex_param("Normal", 200, "/Engine/EngineMaterials/DefaultNormal", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    r = tex_param("Roughness", 600, "/Engine/EngineResources/DefaultTexture", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    fc, fn_, fr = wat(fwt, c, -400), wat(fwn, n, 200), wat(fwt, r, 600)
    tint = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, -600); tint.set_editor_property("parameter_name", "Tint"); tint.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
    mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, -400); MEL.connect_material_expressions(fc, "XYZ Texture", mul, "A"); MEL.connect_material_expressions(tint, "", mul, "B")
    wet = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -500, 800); wet.set_editor_property("parameter_name", "RoughnessMul"); wet.set_editor_property("default_value", 1.0)
    mr = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 600); MEL.connect_material_expressions(fr, "XYZ Texture", mr, "A"); MEL.connect_material_expressions(wet, "", mr, "B")
    met = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -300, 400); met.set_editor_property("parameter_name", "Metallic"); met.set_editor_property("default_value", 0.0)
    MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(fn_, "XYZ Texture", unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(mr, "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(met, "", unreal.MaterialProperty.MP_METALLIC)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def instance(name, parent, tx, tint=(1, 1, 1), rough=1.0, metal=0.0, tile=300.0):
    p = f"{MAT}/MI_{name}"
    mi = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(f"MI_{name}", MAT, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    for k, v in (("BaseColor", "Color"), ("Normal", "NormalDX"), ("Roughness", "Roughness")):
        if v in tx: MEL.set_material_instance_texture_parameter_value(mi, k, tx[v])
    MEL.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(*tint, 1))
    MEL.set_material_instance_scalar_parameter_value(mi, "RoughnessMul", rough); MEL.set_material_instance_scalar_parameter_value(mi, "Metallic", metal)
    MEL.set_material_instance_scalar_parameter_value(mi, "TileSize", tile); EAL.save_loaded_asset(mi, False); return p
def run():
    m = master(); out = {}
    look = {  # name: (tint, roughness mul (wet = low), metallic, tile)
        "Concrete034": ((0.55, 0.62, 0.66), 0.55, 0.0, 400.0), "Concrete044A": ((0.5, 0.55, 0.58), 0.6, 0.0, 300.0),
        "CorrugatedSteel005": ((0.45, 0.5, 0.52), 0.6, 0.8, 250.0), "Ground037": ((0.6, 0.55, 0.5), 0.45, 0.0, 350.0), "Ground080": ((0.55, 0.5, 0.45), 0.4, 0.0, 300.0),
        "Grass004": ((0.6, 0.68, 0.62), 0.8, 0.0, 300.0), "Rock030": ((0.6, 0.64, 0.68), 0.7, 0.0, 600.0), "Rock035": ((0.55, 0.6, 0.65), 0.7, 0.0, 600.0),
        "PaintedPlaster017": ((0.85, 0.8, 0.75), 1.0, 0.0, 250.0), "Bricks059": ((0.6, 0.6, 0.62), 0.7, 0.0, 300.0), "Asphalt031": ((0.5, 0.52, 0.55), 0.5, 0.0, 400.0)}
    for s in SETS:
        tx = textures(s); t, r, me, tl = look[s]; out[s] = instance(s, m, tx, t, r, me, tl)
    return out
