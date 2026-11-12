import unreal, importlib, random
import tum_art as A; importlib.reload(A)
import tum_s91 as S; importlib.reload(S)
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); V = unreal.Vector
def msmi(name, folder, d, n, orm, tile, tint=(1, 1, 1)):
    p = f"{S.MATP}/MI_W_{name}"
    x = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(f"MI_W_{name}", S.MATP, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(x, S.master_orm()); base = f"/Game/MS/Surfaces/{folder}/"
    MEL.set_material_instance_texture_parameter_value(x, "BaseColor", EAL.load_asset(base + d)); MEL.set_material_instance_texture_parameter_value(x, "Normal", EAL.load_asset(base + n))
    MEL.set_material_instance_texture_parameter_value(x, "ORM", EAL.load_asset(base + orm))
    MEL.set_material_instance_scalar_parameter_value(x, "TileSize", tile); MEL.set_material_instance_scalar_parameter_value(x, "MetallicMul", 0.0); MEL.set_material_instance_scalar_parameter_value(x, "RoughnessMul", 0.75)
    MEL.set_material_instance_vector_parameter_value(x, "Tint", unreal.LinearColor(*tint, 1)); EAL.save_loaded_asset(x, False); return x
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    grav = msmi("Gravel", "Gravel_Ground_vi0maebg", "T_Gravel_Ground_vi0maebg_D", "T_Gravel_Ground_vi0maebg_N", "T_GravelGround_vi0maebg_ORDp", 350.0, (0.75, 0.75, 0.75))
    soil = msmi("RockySoil", "Rocky_Soil_Ground_vb2qdgwew", "T_Rocky_Soil_Ground_vb2qdgwew_D", "T_Rocky_Soil_Ground_vb2qdgwew_N", "T_RockySoilGround_vb2qdgwew_ORDp", 400.0, (0.7, 0.7, 0.7))
    burnt = msmi("BurntGrass", "Burnt_Grass_smlmnnn", "T_Burnt_Grass_smlmnnn_D", "T_Burnt_Grass_smlmnnn_N", "T_BurntGrass_smlmnnn_DpRA", 300.0, (0.6, 0.65, 0.6))
    A.LES().load_level("/Game/TUM/Maps/M_FactoryHub")
    for a in A.EAS().get_all_level_actors():
        if unreal.Name("ArtPass") in a.tags and str(a.get_folder_path()).startswith("Art/Exterior/Ground"): A.EAS().destroy_actor(a)
        if a.get_actor_label() == "Ext_Ground": a.static_mesh_component.set_material(0, grav)
    rnd = random.Random(21); G = "Art/Exterior/Ground"; cube = EAL.load_asset("/Engine/BasicShapes/Cube")
    # irregular soil / dead-grass / old concrete patches on top of the gravel yard (breaks the flat floor)
    for i in range(46):
        mat = (soil, burnt, EAL.load_asset(f"{S.MATP}/MI_W_FloorDirty"))[i % 3]
        x, y = rnd.uniform(-6800, -1400), rnd.uniform(-4800, 4800); sx, sy = rnd.uniform(400, 1400), rnd.uniform(300, 1100)
        p = A.EAS().spawn_actor_from_object(cube, V(x, y, 0.6 + i * 0.05), unreal.Rotator(roll=0, pitch=0, yaw=rnd.uniform(0, 180)))
        p.set_actor_scale3d(V(sx / 100, sy / 100, 0.02)); p.static_mesh_component.set_material(0, mat); p.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        p.set_actor_label(f"Ground_Patch_{i}"); p.set_folder_path(G); p.tags = [unreal.Name("ArtPass")]
    # broken slabs, rubble mounds, gravel patches, puddles, junk
    A.scatter(["Broken_Concrete_Slab", "Concrete_Rubble_Pile_ujriaadga_01", "Concrete_Rubble_Pile_ujriaadga_02", "Cement_Rubble", "SM_Ind_Con_Pile_Rubble_Gravel_Patch_01", "SM_Ind_Rubble_Pile_Debris_Concrete_M_05", "SM_Ind_Rubble_Debris_Pile_Gravel_M_01"], 60, -6900, -1300, -4900, 4900, seed=22, smin=0.7, smax=1.6, folder=G)
    A.scatter(["SM_Water_M_01", "SM_Water_Small"], 12, -6500, -1500, -4500, 4500, z=1.5, seed=23, smin=0.8, smax=2.0, folder=G)
    A.scatter(["Old_Wood_Boards_ricaS_00", "Old_Wood_Boards_ricaS_02", "Worn_Wooden_Beam", "SM_Ind_Con_Supplies_Beam_Metal_Rusty_02", "Pile_Of_Chains", "SM_Ind_Ware_Storage_Sheet_Cardboard_Flat_06_B", "SM_Urb_Road_Sheet_Metal_Rusty_03"], 34, -6800, -1400, -4800, 4800, seed=24, folder=G)
    A.scatter(["SM_rbdoo_VarA", "SM_rbdoo_VarB", "SM_rbdoo_VarC", "Dry_Grass_tbbqejqr_01", "Dry_Grass_tbbqejqr_03", "Dry_Grass_tbbqejqr_05"], 260, -6950, -1250, -4950, 4950, seed=25, smin=0.7, smax=1.6, folder=G)
    for i in range(70):  # weeds along the facade foot and the yard edges
        x = rnd.uniform(-1500, -1250) if i % 2 else rnd.uniform(-6950, -6700); y = rnd.uniform(-4900, 4900)
        A.place(("SM_rbdoo_VarA", "Dry_Grass_tbbqejqr_02", "SM_rbdoo_VarC")[i % 3], x, y, 0, scale=rnd.uniform(1.0, 1.8), yaw=rnd.uniform(0, 360), folder=G)
    A.LES().save_current_level()
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(V(-6200, -1500, 250), unreal.Rotator(roll=0, pitch=-6, yaw=20))
    return "ok"
