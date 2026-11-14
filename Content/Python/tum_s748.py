# Factory materials: the triplanar master shows a checker on vertical faces, so every factory MI moves to the world-aligned
# master (engine WorldAlignedTexture) and the walls get the real brick set.
import unreal, importlib, traceback
import tum_fac as K; importlib.reload(K)
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; E = K.E; L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); MS = K.MS
TX = "/Game/TUM/Textures/Surfaces/Bricks059/Bricks059_1K-JPG_"
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_FactoryHub"); out = {}
    master = EAL.load_asset(f"{MS}/MAT_SurfaceWorldORM"); out["master"] = master.get_name() if master else None
    for n in ("MI_W_SteelDark", "MI_W_RailPaint", "MI_W_Grate", "MI_W_RoofSheet", "MI_W_FloorWet"):
        m = EAL.load_asset(f"{MS}/{n}"); MEL.set_material_instance_parent(m, master); EAL.save_loaded_asset(m, False)
    def make(name, color, normal, tile, rough, tint):
        p = f"{MS}/{name}"
        if not EAL.does_asset_exist(p): EAL.duplicate_asset(f"{MS}/MI_W_WallPainted", p)
        m = EAL.load_asset(p); MEL.set_material_instance_parent(m, master)
        MEL.set_material_instance_texture_parameter_value(m, "BaseColor", EAL.load_asset(color))
        MEL.set_material_instance_texture_parameter_value(m, "Normal", EAL.load_asset(normal))
        MEL.set_material_instance_texture_parameter_value(m, "ORM", EAL.load_asset("/Engine/EngineResources/WhiteSquareTexture"))
        for k, v in (("TileSize", tile), ("RoughnessMul", rough), ("MetallicMul", 0.0)): MEL.set_material_instance_scalar_parameter_value(m, k, v)
        MEL.set_material_instance_vector_parameter_value(m, "Tint", unreal.LinearColor(tint[0], tint[1], tint[2], 1)); EAL.save_loaded_asset(m, False); return m
    brick = make("MI_W_FacBrick", TX + "Color", TX + "NormalDX", 260.0, 0.9, (0.75, 0.7, 0.66))
    wp = EAL.load_asset(f"{MS}/MI_W_WallPainted")
    conc = make("MI_W_FacConcrete", MEL.get_material_instance_texture_parameter_value(wp, "BaseColor").get_path_name(), "/Engine/EngineMaterials/DefaultNormal", 350.0, 0.9, (0.7, 0.7, 0.7))
    n = {"brick": 0, "conc": 0}
    for a in E.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor): continue
        c = a.static_mesh_component; m = c.get_material(0); nm = m.get_name() if m else ""; lab = a.get_actor_label()
        if unreal.Name(K.TAG) in a.tags and nm in ("MI_Bricks059", "MI_W_WallOld", "MI_W_WallDado", "MI_W_WallPainted", "MI_W_FacBrick", "MI_W_FacConcrete"):
            if "dado" in lab or "lintel" in lab or "sill" in lab or "Plinth" in lab: c.set_material(0, conc); n["conc"] += 1
            else: c.set_material(0, brick); n["brick"] += 1
        elif nm == "MI_W_WallPainted" and c.static_mesh and c.static_mesh.get_name() == "Cube": c.set_material(0, conc); n["conc"] += 1
    out["n"] = n; L.save_current_level(); return out
