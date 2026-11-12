# Real 3D night city (Fab "LA Night City", photogrammetry) outside the bedroom window
import unreal
EAL = unreal.EditorAssetLibrary; V = unreal.Vector
def E(): return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def place(scale=30.0, loc=(0, 45000, -6500), yaw=0.0):
    for a in E().get_all_level_actors():
        if a.get_actor_label().startswith("City3D_"): E().destroy_actor(a)
    meshes = [EAL.load_asset(p) for p in EAL.list_assets("/Game/TUM/Environment/City", True, False) if isinstance(EAL.load_asset(p), unreal.StaticMesh)]
    for i, m in enumerate(meshes):
        try:
            ns = m.get_editor_property("nanite_settings"); ns.enabled = True; m.set_editor_property("nanite_settings", ns); EAL.save_loaded_asset(m, False)
        except Exception: pass
        a = E().spawn_actor_from_object(m, V(*loc), unreal.Rotator(roll=0, pitch=0, yaw=yaw)); a.set_actor_scale3d(V(scale, scale, scale))
        c = a.static_mesh_component; c.set_collision_profile_name("NoCollision"); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); c.set_cast_shadow(False)
        a.set_actor_label(f"City3D_{i}"); a.set_folder_path("Art/City"); a.tags = [unreal.Name("ArtPass")]
    for a in E().get_all_level_actors():
        if a.get_actor_label() == "City_Dome": a.set_actor_scale3d(V(3000, 3000, 3000)); a.set_actor_location(V(0, 0, -20000), False, False)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return len(meshes)
MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
def unlit(intensity=2.5):
    mp = "/Game/TUM/Materials/Surfaces/M_CityUnlit"
    if not EAL.does_asset_exist(mp):
        m = AT.create_asset("M_CityUnlit", "/Game/TUM/Materials/Surfaces", unreal.Material, unreal.MaterialFactoryNew())
        m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        s = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -600, 0); s.set_editor_property("parameter_name", "Tex")
        k = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -600, 250); k.set_editor_property("parameter_name", "Intensity"); k.set_editor_property("default_value", intensity)
        mu = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 0); MEL.connect_material_expressions(s, "RGB", mu, "A"); MEL.connect_material_expressions(k, "", mu, "B")
        MEL.connect_material_property(mu, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR); MEL.recompile_material(m); EAL.save_loaded_asset(m, False)
    parent = EAL.load_asset(mp); done = {}
    for a in E().get_all_level_actors():
        if not a.get_actor_label().startswith("City3D_"): continue
        c = a.static_mesh_component
        for i in range(c.get_num_materials()):
            om = c.get_material(i); key = om.get_name() if om else "none"
            if key not in done:
                tex = None
                vals = om.get_editor_property("texture_parameter_values") if isinstance(om, unreal.MaterialInstance) else []
                for v in vals:
                    nm = str(v.parameter_info.name).lower()
                    if tex is None or "base" in nm or "color" in nm or "diffuse" in nm: tex = v.parameter_value
                    if "base" in nm or "color" in nm: break
                n = "MI_City_" + key[:40]; p = "/Game/TUM/Environment/City/" + n
                if EAL.does_asset_exist(p) and not key.startswith("MI_City_"):
                    done[key] = EAL.load_asset(p); c.set_material(i, done[key]); continue
                if key.startswith("MI_City_"): done[key] = om; continue
                mi = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(n, "/Game/TUM/Environment/City", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                MEL.set_material_instance_parent(mi, parent)
                if tex: MEL.set_material_instance_texture_parameter_value(mi, "Tex", tex)
                MEL.set_material_instance_scalar_parameter_value(mi, "Intensity", intensity); EAL.save_loaded_asset(mi, False); done[key] = mi
            c.set_material(i, done[key])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return len(done)
def place_multi(spots, scale=30.0, prefix="City3D_"):
    for a in E().get_all_level_actors():
        if a.get_actor_label().startswith(prefix): E().destroy_actor(a)
    meshes = [EAL.load_asset(p) for p in EAL.list_assets("/Game/TUM/Environment/City/LANightCity", True, False) if isinstance(EAL.load_asset(p), unreal.StaticMesh)]
    n = 0
    for (loc, yaw) in spots:
        for m in meshes:
            a = E().spawn_actor_from_object(m, V(*loc), unreal.Rotator(roll=0, pitch=0, yaw=yaw)); a.set_actor_scale3d(V(scale, scale, scale))
            c = a.static_mesh_component; c.set_collision_profile_name("NoCollision"); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); c.set_cast_shadow(False)
            a.set_actor_label(f"{prefix}{n}"); a.set_folder_path("Art/City"); a.tags = [unreal.Name("ArtPass")]; n += 1
    return n
