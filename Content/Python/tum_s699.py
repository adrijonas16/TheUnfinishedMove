# Dragon look + seat: the Fab material read the packed texture as fully metallic (mirror-like skin). Own matte material using the
# same textures (override on the level actor only, the Fab asset is untouched), dragon 1.45x bigger, rider seated at the shoulders,
# canyon walls 250 cm further out for the wider wings.
import unreal, traceback
import tum_s291 as D
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); V = unreal.Vector
TEX = "/Game/Fab/Prowler_Dragon_Variant_Rig/prowler_dragon_variant_rig/Textures/prowler_dragon_variant_rig_texture_%d"
MD = "/Game/TUM/Materials/Dragon"; SCALE = 0.158; OFFX = -150.0; OFFZ = -445.0
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def skin(bright=1.3):
    p = f"{MD}/M_DragonSkin"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_DragonSkin", MD, unreal.Material, unreal.MaterialFactoryNew()); ex, con = D.ex, D.con
    m.set_editor_property("used_with_skeletal_mesh", True)
    b = ex(m, unreal.MaterialExpressionTextureSample, -700, -200, texture=EAL.load_asset(TEX % 0))
    k = ex(m, unreal.MaterialExpressionScalarParameter, -700, -40, parameter_name="Bright", default_value=bright)
    mu = ex(m, unreal.MaterialExpressionMultiply, -420, -160); con(b, "RGB", mu, "A"); con(k, "", mu, "B")
    MEL.connect_material_property(mu, "", unreal.MaterialProperty.MP_BASE_COLOR)
    n = ex(m, unreal.MaterialExpressionTextureSample, -700, 420, texture=EAL.load_asset(TEX % 2), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    MEL.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL)
    o = ex(m, unreal.MaterialExpressionTextureSample, -700, 120, texture=EAL.load_asset(TEX % 1), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    lo = ex(m, unreal.MaterialExpressionConstant, -420, 60, r=0.62); hi = ex(m, unreal.MaterialExpressionConstant, -420, 120, r=0.95)
    lp = ex(m, unreal.MaterialExpressionLinearInterpolate, -220, 100); con(lo, "", lp, "A"); con(hi, "", lp, "B"); con(o, "G", lp, "Alpha")
    MEL.connect_material_property(lp, "", unreal.MaterialProperty.MP_ROUGHNESS)
    me = ex(m, unreal.MaterialExpressionConstant, -220, 260, r=0.0); MEL.connect_material_property(me, "", unreal.MaterialProperty.MP_METALLIC)
    sp = ex(m, unreal.MaterialExpressionConstant, -220, 330, r=0.25); MEL.connect_material_property(sp, "", unreal.MaterialProperty.MP_SPECULAR)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def apply():
    out = {}
    m = skin()
    ps = [a for a in E.get_all_level_actors() if isinstance(a, unreal.PlayerStart)][0].get_actor_location()
    d = [a for a in E.get_all_level_actors() if a.get_actor_label() == "Dragon_Mesh"][0]; c = d.skeletal_mesh_component
    out["old_mats"] = [str(c.get_material(i).get_class().get_name()) + ":" + c.get_material(i).get_name() for i in range(c.get_num_materials())]
    for i in range(c.get_num_materials()): c.set_material(i, m)
    d.set_actor_scale3d(V(SCALE, SCALE, SCALE)); d.set_actor_location(V(ps.x + OFFX, ps.y, ps.z + OFFZ), False, False); d.set_actor_enable_collision(False)
    o, e = d.get_actor_bounds(False); out["dragon_bounds"] = [[round(v) for v in o.to_tuple()], [round(v) for v in e.to_tuple()]]
    moved = 0; sw = {}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("Wall_") and "TUMWide" not in [str(t) for t in a.tags]:
            l = a.get_actor_location(); a.set_actor_location(V(l.x, l.y + (250 if l.y > 0 else -250), l.z), False, False)
            a.tags = list(a.tags) + [unreal.Name("TUMWide")]; moved += 1
        if lab.startswith("StormWall_") or lab in ("Kill_Floor", "Start_Floor"):
            o, e = a.get_actor_bounds(False); sw[lab] = [[round(v) for v in o.to_tuple()], [round(v) for v in e.to_tuple()]]
    out["walls_moved"] = moved; out["blockers"] = sw
    L.save_current_level(); return out
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon"); step("apply", apply); return res
