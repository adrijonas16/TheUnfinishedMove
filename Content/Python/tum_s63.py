import unreal
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
S = r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\fab"
def imp(fn, dest):
    t = unreal.AssetImportTask(); t.filename = fn; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
    AT.import_asset_tasks([t]); return list(t.imported_object_paths)
def run():
    out = {}
    for name, fn, dest in (("Facade", S + r"\facade\source\FBX_1_mln_2x16K_N\FBX_1_mln_2x16K_N.fbx", "/Game/TUM/Environment/Facade"),
                           ("Kaarina", S + r"\Kaarina.glb", "/Game/TUM/Environment/Kaarina"),
                           ("Interior", S + r"\WarehouseInterior.glb", "/Game/TUM/Environment/WarehouseInterior")):
        paths = imp(fn, dest); info = []
        for p in paths:
            a = EAL.load_asset(p)
            if isinstance(a, unreal.Texture2D):
                a.set_editor_property("max_texture_size", 4096); EAL.save_loaded_asset(a, False)
            if isinstance(a, unreal.StaticMesh):
                bb = a.get_bounding_box(); info.append((p, round(bb.max.x - bb.min.x), round(bb.max.y - bb.min.y), round(bb.max.z - bb.min.z), round(bb.min.z)))
        out[name] = {"n": len(paths), "meshes": info[:40], "nmesh": len(info)}
    return out
