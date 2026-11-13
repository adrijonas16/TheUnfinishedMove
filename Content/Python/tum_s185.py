# Robust triplanar masters (replace the world-aligned function that rendered as checkerboards)
import unreal
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); MV = "/Game/TUM/Materials/Surfaces"
X = unreal.MaterialExpression
def ex(m, cls, x, y, **props):
    e = MEL.create_material_expression(m, cls, x, y)
    for k, v in props.items(): e.set_editor_property(k, v)
    return e
def con(a, ao, b, bi): MEL.connect_material_expressions(a, ao, b, bi)
def build(name, orm):
    p = f"{MV}/{name}"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset(name, MV, unreal.Material, unreal.MaterialFactoryNew())
    wp = ex(m, unreal.MaterialExpressionWorldPosition, -2200, 0)
    tile = ex(m, unreal.MaterialExpressionScalarParameter, -2200, 200, parameter_name="TileSize", default_value=300.0)
    div = ex(m, unreal.MaterialExpressionDivide, -2000, 0); con(wp, "", div, "A"); con(tile, "", div, "B")
    uvs = {}
    for i, (axes) in enumerate((("r", "g"), ("r", "b"), ("g", "b"))):
        mk = ex(m, unreal.MaterialExpressionComponentMask, -1800, i * 150, r=("r" in axes), g=("g" in axes), b=("b" in axes)); con(div, "", mk, ""); uvs[i] = mk
    nrm = ex(m, unreal.MaterialExpressionVertexNormalWS, -2200, 600)
    ab = ex(m, unreal.MaterialExpressionAbs, -2000, 600); con(nrm, "", ab, "")
    pw = ex(m, unreal.MaterialExpressionPower, -1850, 600, const_exponent=6.0); con(ab, "", pw, "Base")
    wz = ex(m, unreal.MaterialExpressionComponentMask, -1650, 550, b=True); con(pw, "", wz, "")
    wy = ex(m, unreal.MaterialExpressionComponentMask, -1650, 650, g=True); con(pw, "", wy, "")
    wx = ex(m, unreal.MaterialExpressionComponentMask, -1650, 750, r=True); con(pw, "", wx, "")
    s1 = ex(m, unreal.MaterialExpressionAdd, -1500, 650); con(wz, "", s1, "A"); con(wy, "", s1, "B")
    s2 = ex(m, unreal.MaterialExpressionAdd, -1400, 700); con(s1, "", s2, "A"); con(wx, "", s2, "B")
    w = {}
    for k, c in (("z", wz), ("y", wy), ("x", wx)):
        d = ex(m, unreal.MaterialExpressionDivide, -1250, 600 + len(w) * 100); con(c, "", d, "A"); con(s2, "", d, "B"); w[k] = d
    def tri(pname, default, st, y):
        t = ex(m, unreal.MaterialExpressionTextureObjectParameter, -1600, y, parameter_name=pname, texture=EAL.load_asset(default), sampler_type=st)
        outs = []
        for i, k in ((0, "z"), (1, "y"), (2, "x")):
            s = ex(m, unreal.MaterialExpressionTextureSample, -1200, y + i * 120); con(t, "", s, "Tex"); con(uvs[i], "", s, "UVs")
            mul = ex(m, unreal.MaterialExpressionMultiply, -1000, y + i * 120); con(s, "RGB", mul, "A"); con(w[k], "", mul, "B"); outs.append(mul)
        a1 = ex(m, unreal.MaterialExpressionAdd, -850, y); con(outs[0], "", a1, "A"); con(outs[1], "", a1, "B")
        a2 = ex(m, unreal.MaterialExpressionAdd, -750, y); con(a1, "", a2, "A"); con(outs[2], "", a2, "B"); return a2
    col = tri("BaseColor", "/Engine/EngineResources/DefaultTexture", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, 1000)
    tint = ex(m, unreal.MaterialExpressionVectorParameter, -750, 900, parameter_name="Tint", default_value=unreal.LinearColor(1, 1, 1, 1))
    cm = ex(m, unreal.MaterialExpressionMultiply, -600, 1000); con(col, "", cm, "A"); con(tint, "", cm, "B")
    MEL.connect_material_property(cm, "", unreal.MaterialProperty.MP_BASE_COLOR)
    nm = tri("Normal", "/Engine/EngineMaterials/DefaultNormal", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, 1500)
    MEL.connect_material_property(nm, "", unreal.MaterialProperty.MP_NORMAL)
    rmul = ex(m, unreal.MaterialExpressionScalarParameter, -750, 2300, parameter_name="RoughnessMul", default_value=1.0)
    if orm:
        o = tri("ORM", "/Engine/EngineResources/WhiteSquareTexture", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR, 2000)
        g = ex(m, unreal.MaterialExpressionComponentMask, -600, 2000, g=True); con(o, "", g, "")
        bb = ex(m, unreal.MaterialExpressionComponentMask, -600, 2100, b=True); con(o, "", bb, "")
        r = ex(m, unreal.MaterialExpressionMultiply, -450, 2000); con(g, "", r, "A"); con(rmul, "", r, "B")
        mm = ex(m, unreal.MaterialExpressionScalarParameter, -600, 2200, parameter_name="MetallicMul", default_value=1.0)
        me = ex(m, unreal.MaterialExpressionMultiply, -450, 2150); con(bb, "", me, "A"); con(mm, "", me, "B")
        MEL.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS); MEL.connect_material_property(me, "", unreal.MaterialProperty.MP_METALLIC)
    else:
        o = tri("Roughness", "/Engine/EngineResources/WhiteSquareTexture", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR, 2000)
        g = ex(m, unreal.MaterialExpressionComponentMask, -600, 2000, r=True); con(o, "", g, "")
        r = ex(m, unreal.MaterialExpressionMultiply, -450, 2000); con(g, "", r, "A"); con(rmul, "", r, "B")
        mt = ex(m, unreal.MaterialExpressionScalarParameter, -600, 2200, parameter_name="Metallic", default_value=0.0)
        MEL.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS); MEL.connect_material_property(mt, "", unreal.MaterialProperty.MP_METALLIC)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def run():
    a = build("MAT_TriplanarORM", True); b = build("MAT_Triplanar", False); n = 0
    for p in EAL.list_assets(MV, False, False):
        mi = EAL.load_asset(p)
        if isinstance(mi, unreal.MaterialInstanceConstant):
            par = mi.get_editor_property("parent"); pn = par.get_name() if par else ""
            if pn == "MAT_SurfaceWorldORM": MEL.set_material_instance_parent(mi, a); EAL.save_loaded_asset(mi, False); n += 1
            elif pn == "MAT_SurfaceWorld": MEL.set_material_instance_parent(mi, b); EAL.save_loaded_asset(mi, False); n += 1
    return n
