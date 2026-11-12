import unreal, os, json, urllib.request, importlib
import tum_ph as PH; importlib.reload(PH)
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); V = unreal.Vector
def backdrop(hdri="rooftop_night"):
    files = json.loads(PH._get(f"https://api.polyhaven.com/files/{hdri}"))
    url = files["tonemapped"]["url"]; d = os.path.join(PH.ROOT, hdri); os.makedirs(d, exist_ok=True); p = os.path.join(d, f"{hdri}.jpg"); open(p, "wb").write(PH._get(url))
    t = unreal.AssetImportTask(); t.filename = p; t.destination_path = "/Game/TUM/Environment/Backdrops"; t.automated = True; t.replace_existing = True; t.save = True
    AT.import_asset_tasks([t]); tex = EAL.load_asset(t.imported_object_paths[0])
    mp = "/Game/TUM/Materials/Surfaces/MAT_CityBackdrop"
    if EAL.does_asset_exist(mp): EAL.delete_asset(mp)
    m = AT.create_asset("MAT_CityBackdrop", "/Game/TUM/Materials/Surfaces", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT); m.set_editor_property("two_sided", True)
    s = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -600, 0); s.set_editor_property("parameter_name", "Sky"); s.set_editor_property("texture", tex)
    k = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -600, 250); k.set_editor_property("parameter_name", "Intensity"); k.set_editor_property("default_value", 1.0)
    mu = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 0); MEL.connect_material_expressions(s, "RGB", mu, "A"); MEL.connect_material_expressions(k, "", mu, "B")
    MEL.connect_material_property(mu, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR); MEL.recompile_material(m); EAL.save_loaded_asset(m, False)
    return m
def place_dome(m, center, radius=6000.0, yaw=0.0, label="City_Dome"):
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == label: eas.destroy_actor(a)
    a = eas.spawn_actor_from_object(EAL.load_asset("/Engine/BasicShapes/Sphere"), center, unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    a.set_actor_scale3d(V(radius / 50, radius / 50, radius / 50)); a.static_mesh_component.set_material(0, m)
    a.static_mesh_component.set_collision_profile_name("NoCollision"); a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); a.set_actor_enable_collision(False); a.static_mesh_component.set_cast_shadow(False)
    a.set_actor_label(label); a.set_folder_path("Art/City"); a.tags = [unreal.Name("ArtPass")]
    return a
