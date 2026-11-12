# Real Room v3: dark room (moon + city light), rain, bigger far dome, chair faces desk and can be pushed, wardrobe doors, entry door
import unreal, importlib
import tum_lib as T; importlib.reload(T)
import tum_art as A; importlib.reload(A)
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); V = unreal.Vector
MV = "/Game/TUM/Materials/Surfaces"
def E(): return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def find(label): return [a for a in E().get_all_level_actors() if a.get_actor_label() == label]
def kill(labels):
    for a in E().get_all_level_actors():
        if a.get_actor_label() in labels: E().destroy_actor(a)
def rain_mat(name, opacity, speed, tile_u, tile_v, glass=False):
    p = f"{MV}/{name}"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset(name, MV, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT); m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT); m.set_editor_property("two_sided", True)
    tc = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1100, 0); tc.set_editor_property("u_tiling", tile_u); tc.set_editor_property("v_tiling", tile_v)
    pn = MEL.create_material_expression(m, unreal.MaterialExpressionPanner, -900, 0); pn.set_editor_property("speed_x", 0.0); pn.set_editor_property("speed_y", -speed)
    MEL.connect_material_expressions(tc, "", pn, "Coordinate")
    tx = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 0); tx.set_editor_property("texture", EAL.load_asset("/Engine/EngineMaterials/Good64x64TilingNoiseHighFreq")); tx.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
    MEL.connect_material_expressions(pn, "", tx, "UVs")
    pw = MEL.create_material_expression(m, unreal.MaterialExpressionPower, -500, 0); pw.set_editor_property("const_exponent", 6.0 if not glass else 10.0)
    MEL.connect_material_expressions(tx, "R", pw, "Base")
    op = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 100); op.set_editor_property("const_b", opacity)
    MEL.connect_material_expressions(pw, "", op, "A")
    col = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -300, -150); col.set_editor_property("constant", unreal.LinearColor(0.55, 0.65, 0.8, 1))
    em = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -150, -100); MEL.connect_material_expressions(col, "", em, "A"); MEL.connect_material_expressions(pw, "", em, "B")
    MEL.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR); MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def run():
    W = "Room/Window"
    # rain: two sheets outside + streaks on the glass
    kill(["Rain_Near", "Rain_Far", "Rain_Glass", "Moon", "City_Glow", "Room_Fill", "Window_Light", "Door_Slab", "Door_Frame_L", "Door_Frame_R", "Door_Frame_T", "Door_Handle", "Room_Wall_S", "Room_Wall_S_L", "Room_Wall_S_R", "Room_Wall_S_T", "Wardrobe_Doors"])
    near = rain_mat("M_RainSheetNear", 1.0, 2.2, 8.0, 1.2); far = rain_mat("M_RainSheetFar", 0.35, 1.4, 14.0, 3.0); gl = rain_mat("M_RainGlass", 0.35, 0.08, 3.0, 1.0, glass=True)
    T.box("Rain_Near", -400, 400, 420, 421, -200, 500, near, W, collide=False)
    T.box("Rain_Far", -1500, 1500, 1200, 1201, -800, 1200, far, W, collide=False)
    T.box("Rain_Glass", -154, 154, 305, 306, 81, 239, gl, W, collide=False)
    # far city dome: huge radius so it has no parallax up close
    for a in find("City_Dome"):
        a.set_actor_scale3d(V(2000, 2000, 2000)); a.set_actor_location(V(0, 0, -15000), False, False)
    # lighting: dark room, moonlight + cold city glow through the window, small warm practicals
    moon = E().spawn_actor_from_class(unreal.DirectionalLight, V(0, 400, 400), unreal.Rotator(roll=0, pitch=-32, yaw=-100))
    lc = moon.get_component_by_class(unreal.LightComponent); lc.set_intensity(1.2); lc.set_light_color(unreal.LinearColor(0.55, 0.68, 1.0, 1))
    T.tag(moon, "Moon", "Room/Lights")
    rl = E().spawn_actor_from_class(unreal.RectLight, V(0, 330, 160), unreal.Rotator(roll=0, pitch=0, yaw=-90))
    rc = rl.get_component_by_class(unreal.RectLightComponent); rc.set_intensity(18.0); rc.set_light_color(unreal.LinearColor(0.45, 0.5, 0.85, 1))
    rc.set_editor_property("source_width", 300.0); rc.set_editor_property("source_height", 160.0); rc.set_editor_property("attenuation_radius", 900.0)
    T.tag(rl, "City_Glow", "Room/Lights")
    for a in E().get_all_level_actors():
        l = a.get_actor_label()
        if l == "Lamp_Light": a.get_component_by_class(unreal.LightComponent).set_intensity(60.0)
        if l == "Bed_Light": a.get_component_by_class(unreal.LightComponent).set_intensity(40.0)
    # chair: face the desk, movable, can be pushed
    for a in find("Desk_Chair"):
        a.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=0), False)
        c = a.static_mesh_component; c.set_mobility(unreal.ComponentMobility.MOVABLE); c.set_simulate_physics(True); c.set_mass_override_in_kg("", 12.0, True)
        c.set_linear_damping(2.0); c.set_angular_damping(4.0)
    # wardrobe sliding doors at the same transform
    for a in find("Wardrobe"):
        d = E().spawn_actor_from_object(A.mesh("SM_Modern_Cupboard_Sliding_Door"), a.get_actor_location(), a.get_actor_rotation()); d.set_actor_scale3d(a.get_actor_scale3d())
        d.set_actor_label("Wardrobe_Doors"); d.set_folder_path("Room/Furniture"); d.tags = [unreal.Name("ArtPass")]
    # south wall with a doorway + a plain modern interior door (closed)
    wall = f"{MV}/M_WallPaintModern"; trim = f"{MV}/M_WhiteSill"
    T.box("Room_Wall_S_L", -340, 150, -315, -300, 0, 280, wall, "Room"); T.box("Room_Wall_S_R", 245, 340, -315, -300, 0, 280, wall, "Room"); T.box("Room_Wall_S_T", 150, 245, -315, -300, 212, 280, wall, "Room")
    T.box("Door_Frame_L", 144, 150, -318, -297, 0, 212, trim, "Room/Door", collide=False); T.box("Door_Frame_R", 245, 251, -318, -297, 0, 212, trim, "Room/Door", collide=False)
    T.box("Door_Frame_T", 144, 251, -318, -297, 212, 218, trim, "Room/Door", collide=False)
    T.box("Door_Slab", 150, 245, -312, -304, 0, 211, f"{MV}/MI_laminate_floor_02", "Room/Door")
    h = T.box("Door_Handle", 228, 240, -299, -297, 98, 101, f"{MV}/M_BlackAluminum", "Room/Door", collide=False)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return "ok"
