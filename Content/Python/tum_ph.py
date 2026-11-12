# Poly Haven (CC0) downloader + importer, runs inside the editor on the user's PC
import unreal, os, json, urllib.request
ROOT = r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\polyhaven"
AT = unreal.AssetToolsHelpers.get_asset_tools(); EAL = unreal.EditorAssetLibrary
def _get(url): return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "TheUnfinishedMove-jam"}), timeout=60).read()
def download(aid, res="2k"):
    d = os.path.join(ROOT, aid); os.makedirs(d, exist_ok=True)
    files = json.loads(_get(f"https://api.polyhaven.com/files/{aid}"))
    g = files["gltf"][res]["gltf"]
    open(os.path.join(d, f"{aid}.gltf"), "wb").write(_get(g["url"]))
    for rel, info in g.get("include", {}).items():
        p = os.path.join(d, rel.replace("/", os.sep)); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(_get(info["url"]))
    return os.path.join(d, f"{aid}.gltf")
def fetch_and_import(ids, res="2k"):
    out = {}
    for aid in ids:
        try:
            p = download(aid, res)
            t = unreal.AssetImportTask(); t.filename = p; t.destination_path = f"/Game/TUM/Props/PolyHaven/{aid}"; t.automated = True; t.replace_existing = True; t.save = True
            AT.import_asset_tasks([t]); out[aid] = [x for x in t.imported_object_paths if "/StaticMeshes/" in x or isinstance(EAL.load_asset(x), unreal.StaticMesh)][:6]
        except Exception as e: out[aid] = "ERR " + repr(e)[:200]
    return out
