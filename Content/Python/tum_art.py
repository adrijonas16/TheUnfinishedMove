# Art pass helpers: place Megascans / Derelict Corridor meshes over the graybox (decor only, gameplay collision stays on the boxes)
import unreal, random
EAS = lambda: unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LES = lambda: unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
AR = unreal.AssetRegistryHelpers.get_asset_registry(); V = unreal.Vector
_cache = {}
def mesh(sub):
    if not _cache:
        for root in ("/Game/MS/3D", "/Game/DerelictCorridor/Assets"):
            for a in AR.get_assets_by_path(root, recursive=True):
                if str(a.asset_class_path.asset_name) == "StaticMesh": _cache[str(a.asset_name)] = str(a.package_name)
    names = sorted(n for n in _cache if sub.lower() in n.lower())
    if not names: raise KeyError(sub)
    return unreal.load_asset(_cache[names[0]])
def clear(tag="ArtPass"):
    for a in EAS().get_all_level_actors():
        if unreal.Name(tag) in a.tags: EAS().destroy_actor(a)
def place(sub, x, y, z, size=None, scale=None, yaw=0.0, pitch=0.0, roll=0.0, collide=False, folder="Art", label=None, uniform=True, base=True, tags=()):
    m = mesh(sub); bb = m.get_bounding_box(); mn, mx = bb.min, bb.max
    ext = V(max(mx.x - mn.x, 1), max(mx.y - mn.y, 1), max(mx.z - mn.z, 1))
    if size is not None:
        sx, sy, sz = [(size[i] / [ext.x, ext.y, ext.z][i]) if size[i] else None for i in range(3)]
        vals = [s for s in (sx, sy, sz) if s]
        if uniform: s = min(vals); sc = V(s, s, s)
        else: d = sum(vals) / len(vals); sc = V(sx or d, sy or d, sz or d)
    else:
        s = scale or 1.0; sc = V(s, s, s) if not isinstance(scale, (tuple, list)) else V(*scale)
    zoff = -mn.z * sc.z if base else 0.0
    a = EAS().spawn_actor_from_object(m, V(x, y, z + zoff), unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw))
    a.set_actor_scale3d(sc)
    if not collide: a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    a.set_actor_label(label or ("Art_" + sub)); a.set_folder_path(folder); a.tags = [unreal.Name("ArtPass")] + [unreal.Name(t) for t in tags]
    return a
def scatter(subs, n, x0, x1, y0, y1, z=0.0, smin=0.8, smax=1.4, seed=1, folder="Art/Scatter", size=None):
    rnd = random.Random(seed); out = []
    for i in range(n):
        sub = subs[i % len(subs)]; s = rnd.uniform(smin, smax)
        out.append(place(sub, rnd.uniform(x0, x1), rnd.uniform(y0, y1), z, size=None if size is None else tuple(v * s if v else None for v in size), scale=None if size else s, yaw=rnd.uniform(0, 360), folder=folder))
    return out
def hide_box(label_sub):
    n = 0
    for a in EAS().get_all_level_actors():
        if label_sub in a.get_actor_label() and isinstance(a, unreal.StaticMeshActor) and unreal.Name("ArtPass") not in a.tags:
            a.set_actor_hidden_in_game(True); a.static_mesh_component.set_visibility(False); n += 1
    return n
