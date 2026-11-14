# Floating rock shards in the dragon canyon: five Megascans cliff meshes render fans of stray shards high above the rock. Every actor using one of them is replaced by a clean cliff fitted
# to the solid part of the old one. Also re-seats the dragon under the rider (seat constants live in tum_s699).
import unreal, random, traceback, gc
import tum_s679 as W
import tum_s699 as SEAT
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); V = unreal.Vector
AU = unreal.GeometryScript_AssetUtils; MQ = unreal.GeometryScript_MeshQueries; GL = unreal.GeometryScript_List
PREF = ("Wall_", "Rim_", "Horizon_", "Ahead_", "Spur_", "GatePillar_", "Shore_", "Back_Wall", "Start_Cliff", "Beacon_Stack")
# found by hiding one mesh type at a time in Play (the shards are in the Nanite data only, the fallback mesh is clean)
BAD = ("Cliff_vefkehbva", "Cliff_veqnci0db", "Cliff_ulmiccava")
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def _pick(r):
    if not isinstance(r, tuple): return r
    for x in r:
        if not isinstance(x, (unreal.DynamicMesh, bool)): return x
def core_box(sm, trim=0.015):
    dm = unreal.DynamicMesh(); co = unreal.GeometryScriptCopyMeshFromAssetOptions(); lod = unreal.GeometryScriptMeshReadLOD()
    lod.set_editor_property("lod_type", unreal.GeometryScriptLODType.RENDER_DATA); lod.set_editor_property("lod_index", 0)
    fn = getattr(AU, "copy_mesh_from_static_mesh_v2", None) or AU.copy_mesh_from_static_mesh
    fn(sm, dm, co, lod); pl = _pick(MQ.get_all_vertex_positions(dm, False)); P = GL.convert_vector_list_to_array(pl)
    cols = [sorted(p.x for p in P), sorted(p.y for p in P), sorted(p.z for p in P)]; n = len(cols[0]); k = max(1, int(n * trim))
    full = [(c[0], c[-1]) for c in cols]; core = [(c[k], c[n - 1 - k]) for c in cols]
    del P, pl, dm, co, lod
    return full, core, n
def fix():
    random.seed(77); out = {}; used = {}
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor) and a.get_actor_label().startswith(PREF):
            sm = a.static_mesh_component.static_mesh
            if sm: used.setdefault(sm.get_name(), [sm, []])[1].append(a)
    info = {}; bad = {}; clean = []
    for name, (sm, acts) in used.items():
        if any(k in name for k in BAD):
            full, core, n = core_box(sm, 0.002); bad[name] = core; info[name.replace("SM_", "")] = [n, len(acts)]
        elif "Cliff" in name: clean.append(sm)
    out["meshes"] = info; out["bad"] = [n.replace("SM_", "") for n in bad]
    nat = {}
    for m in clean:
        t = E.spawn_actor_from_object(m, V(0, 0, -60000), unreal.Rotator()); o, e = t.get_actor_bounds(False); nat[m.get_name()] = (max(e.x, 1), max(e.y, 1), max(e.z, 1)); E.destroy_actor(t)
    swapped = 0; dist = []
    for name, core in bad.items():
        for a in used[name][1]:
            tf = a.get_actor_transform(); lo = [9e9] * 3; hi = [-9e9] * 3
            for cx in core[0]:
                for cy in core[1]:
                    for cz in core[2]:
                        p = tf.transform_location(V(cx, cy, cz))
                        for j, q in enumerate((p.x, p.y, p.z)): lo[j] = min(lo[j], q); hi[j] = max(hi[j], q)
            sx, sy, sz = [(hi[j] - lo[j]) * 1.06 for j in range(3)]; c = [(hi[j] + lo[j]) / 2 for j in range(3)]
            best = None
            for m in clean:
                ex0, ey0, ez0 = nat[m.get_name()]
                for yaw in (0, 90):
                    s = (sy / (2 * ex0), sx / (2 * ey0), sz / (2 * ez0)) if yaw == 90 else (sx / (2 * ex0), sy / (2 * ey0), sz / (2 * ez0))
                    r = max(s) / min(s) * random.uniform(1.0, 1.12)      # small jitter so neighbours do not all pick the same mesh
                    if best is None or r < best[0]: best = (r, m, yaw)
            lab = a.get_actor_label(); folder = str(a.get_folder_path()); tags = list(a.tags)
            E.destroy_actor(a)
            b = W.fit(best[1], lab, c[0], c[1], c[2] - sz / 2, c[2] + sz / 2, sx, sy, best[2] + random.choice((0, 180)), folder)
            b.tags = tags; swapped += 1; dist.append(round(best[0], 2))
    out["swapped"] = swapped; out["distortion_max_avg"] = [max(dist), round(sum(dist) / len(dist), 2)] if dist else None
    return out
def seat():
    ps = [a for a in E.get_all_level_actors() if isinstance(a, unreal.PlayerStart)][0].get_actor_location()
    d = [a for a in E.get_all_level_actors() if a.get_actor_label() == "Dragon_Mesh"][0]
    d.set_actor_location(V(ps.x + SEAT.OFFX, ps.y, ps.z + SEAT.OFFZ), False, False)
    return [SEAT.OFFX, SEAT.OFFZ]
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon"); step("flakes", fix); step("seat", seat); L.save_current_level()
    gc.collect(); unreal.SystemLibrary.collect_garbage(); return res
