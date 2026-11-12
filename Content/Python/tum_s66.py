import unreal
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
S = r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\fab"
def run():
    out = {}
    for d in ("/Game/TUM/Environment/Kaarina", "/Game/TUM/Environment/WarehouseInterior"):
        if EAL.does_directory_exist(d): EAL.delete_directory(d)
    for name, fn in (("Kaarina", "KaarinaJoined.glb"), ("Interior", "InteriorJoined.glb")):
        t = unreal.AssetImportTask(); t.filename = S + "\\" + fn; t.destination_path = f"/Game/TUM/Environment/{name}"; t.automated = True; t.replace_existing = True; t.save = True
        AT.import_asset_tasks([t]); info = []
        for p in t.imported_object_paths:
            a = EAL.load_asset(p)
            if isinstance(a, unreal.Texture2D): a.set_editor_property("max_texture_size", 4096); EAL.save_loaded_asset(a, False)
            if isinstance(a, unreal.StaticMesh):
                bb = a.get_bounding_box(); info.append((p, [round(v) for v in (bb.min.x, bb.max.x, bb.min.y, bb.max.y, bb.min.z, bb.max.z)]))
        out[name] = info
    return out
