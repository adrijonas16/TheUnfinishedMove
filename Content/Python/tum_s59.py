import unreal
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); V = unreal.Vector
SRC = r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\meshy"
def imp(fn, dest):
    t = unreal.AssetImportTask(); t.filename = f"{SRC}\\{fn}"; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
    AT.import_asset_tasks([t]); paths = list(t.imported_object_paths)
    sm = [p for p in paths if isinstance(EAL.load_asset(p), unreal.StaticMesh)]
    return sm[0] if sm else None, paths
def put(mesh_path, label, x, y, z, height, yaw=0.0, tags=(), hidden=False, folder="Props"):
    m = EAL.load_asset(mesh_path); bb = m.get_bounding_box(); h = max(bb.max.z - bb.min.z, 0.01); s = height / h
    a = EAS.spawn_actor_from_object(m, V(x, y, z - bb.min.z * s), unreal.Rotator(roll=0, pitch=0, yaw=yaw)); a.set_actor_scale3d(V(s, s, s))
    a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    a.set_actor_label(label); a.set_folder_path(folder); a.tags = [unreal.Name("ArtPass")] + [unreal.Name(t) for t in tags]
    if hidden: a.set_actor_hidden_in_game(True)
    return a
def hide_label(lab):
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == lab: a.static_mesh_component.set_visibility(False)
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    knight, kp = imp("KnightWhite.glb", "/Game/TUM/Props/Knight"); seal, sp = imp("SealSilver.glb", "/Game/TUM/Props/Seal")
    out = {"knight": knight, "seal": seal, "kp": kp[:6], "sp": sp[:6]}
    LES.load_level("/Game/TUM/Maps/M_FactoryHub")
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() in ("Knight_Table", "Knight_Pad_Block", "Knight_Pad_Diag", "Knight_Pad_Expose"): EAS.destroy_actor(a)
    put(knight, "Knight_Table", 8800, 30, 80, 22, yaw=90, folder="Art/Factory/Chess")
    for nm, y in (("Block", -350), ("Diag", 0), ("Expose", 350)):
        put(knight, f"Knight_Pad_{nm}", 8410, y, 120 if nm == "Block" else (150 if nm == "Diag" else 180), 55, yaw=180, tags=("ChessPad",), folder="Art/Factory/Chess")
    LES.save_current_level()
    LES.load_level("/Game/TUM/Maps/M_RealRoom")
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == "Knight_Desk_Mesh": EAS.destroy_actor(a)
    hide_label("Knight_Desk"); put(knight, "Knight_Desk_Mesh", 265, -285, 78, 18, yaw=160, tags=("Ending",), hidden=True, folder="Room/Ending")
    LES.save_current_level()
    LES.load_level("/Game/TUM/Maps/M_Cut_WarField")
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() in ("Seal_Hanging_Mesh", "Seal_Ground_Mesh"): EAS.destroy_actor(a)
    hide_label("Seal_Hanging"); hide_label("Seal_Ground")
    h = put(seal, "Seal_Hanging_Mesh", 5900, 0, 340, 70, tags=("WarRope",), folder="Art/War/Shrine"); h.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=0), False)
    g = put(seal, "Seal_Ground_Mesh", 6100, 0, 2, 12, tags=("SealDropped",), hidden=True, folder="Art/War/Shrine")
    LES.save_current_level(); LES.load_level("/Game/TUM/Maps/M_FactoryHub")
    return out
