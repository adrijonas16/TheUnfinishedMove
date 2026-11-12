import unreal, importlib
import tum_s107 as S; importlib.reload(S)
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); EAL = unreal.EditorAssetLibrary
def walls():
    p = S.flat("M_WallPaintModern", (0.42, 0.45, 0.47), 0.0, 0.85); m = EAL.load_asset(p)
    for a in E.get_all_level_actors():
        l = a.get_actor_label()
        if l.startswith("Room_Wall") or l == "Room_Ceiling": a.static_mesh_component.set_material(0, m)
def shot(name, loc, rot, fov=80.0):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "ShotCam": E.destroy_actor(a)
    c = E.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(roll=0, pitch=rot[0], yaw=rot[1])); c.set_actor_label("ShotCam")
    c.camera_component.set_editor_property("field_of_view", fov); c.camera_component.set_editor_property("constrain_aspect_ratio", False)
    unreal.AutomationLibrary.take_high_res_screenshot(1280, 720, rf"C:\UnrealProjects\TheUnfinishedMove\Saved\Shots\{name}.png", camera=c, capture_hdr=False)
MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); MV = "/Game/TUM/Materials/Surfaces"
def floor_mat(tid="laminate_floor_02", tile=180.0):
    name = "M_FloorTop_" + tid; p = f"{MV}/{name}"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset(name, MV, unreal.Material, unreal.MaterialFactoryNew())
    wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1000, 0)
    mk = MEL.create_material_expression(m, unreal.MaterialExpressionComponentMask, -850, 0); mk.set_editor_property("r", True); mk.set_editor_property("g", True); mk.set_editor_property("b", False)
    dv = MEL.create_material_expression(m, unreal.MaterialExpressionDivide, -700, 0); dv.set_editor_property("const_b", tile)
    MEL.connect_material_expressions(wp, "", mk, ""); MEL.connect_material_expressions(mk, "", dv, "A")
    T = f"/Game/TUM/Textures/Surfaces/{tid}"
    def samp(suffix, y, st):
        s = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSample, -450, y); s.set_editor_property("texture", EAL.load_asset(f"{T}/{tid}_{suffix}")); s.set_editor_property("sampler_type", st)
        MEL.connect_material_expressions(dv, "", s, "UVs"); return s
    c = samp("Color", 0, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR); n = samp("NormalDX", 300, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL); r = samp("Roughness", 600, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    MEL.connect_material_property(c, "RGB", unreal.MaterialProperty.MP_BASE_COLOR); MEL.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(r, "R", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def fixes():
    fm = floor_mat()
    cb = EAL.load_asset(f"{MV}/MAT_CityBackdrop")
    for a in E.get_all_level_actors():
        l = a.get_actor_label()
        if l == "Room_Floor": a.static_mesh_component.set_material(0, fm)
        if l == "Desk_Lamp": a.set_actor_scale3d(unreal.Vector(0.6, 0.6, 0.6))
        if l == "Lamp_Light": a.get_component_by_class(unreal.LightComponent).set_intensity(500.0)
        if l == "City_Dome":
            mi = unreal.MaterialInstanceDynamic
    # brighter backdrop via a constant instance
    p = f"{MV}/MI_CityBackdrop"
    mi = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset("MI_CityBackdrop", MV, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, cb); MEL.set_material_instance_scalar_parameter_value(mi, "Intensity", 6.0); EAL.save_loaded_asset(mi, False)
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "City_Dome": a.static_mesh_component.set_material(0, mi)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
