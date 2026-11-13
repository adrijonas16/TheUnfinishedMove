# Unlit text material so every on-screen/world instruction is readable in the dark; hints start hidden
import unreal, traceback
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
P = "/Game/TUM/Materials/M_TextUnlit"
def mat():
    if EAL.does_asset_exist(P): EAL.delete_asset(P)
    m = AT.create_asset("M_TextUnlit", "/Game/TUM/Materials", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property("two_sided", True)
    f = MEL.create_material_expression(m, unreal.MaterialExpressionFontSampleParameter, -600, 0)
    f.set_editor_property("parameter_name", "Font"); f.set_editor_property("font", unreal.load_object(None, "/Engine/EngineFonts/RobotoDistanceField.RobotoDistanceField"))
    vc = MEL.create_material_expression(m, unreal.MaterialExpressionVertexColor, -600, 250)
    k = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -350, 250); k.set_editor_property("const_b", 1.6)
    MEL.connect_material_expressions(vc, "", k, "A")
    MEL.connect_material_property(k, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    a = MEL.create_material_expression(m, unreal.MaterialExpressionComponentMask, -350, 0); a.set_editor_property("a", True)
    MEL.connect_material_expressions(f, "RGBA", a, "")
    MEL.connect_material_property(a, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def run():
    out = {}
    try: m = mat()
    except Exception: return traceback.format_exc()[-800:]
    for mp in ("M_RealRoom", "M_FactoryHub", "M_Cut_Dragon", "M_Cut_WarField", "M_Cut_Cliff"):
        L.load_level(f"/Game/TUM/Maps/{mp}"); n = 0
        for a in E.get_all_level_actors():
            if isinstance(a, unreal.TextRenderActor):
                a.text_render.set_material(0, m); n += 1
                if a.get_actor_label() in ("Hint_Sit", "Hint_Earbuds"): a.set_actor_hidden_in_game(True)
        L.save_current_level(); out[mp] = n
    return out
