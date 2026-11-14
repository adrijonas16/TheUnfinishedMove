# War, shooter-style pass.
# ROOT CAUSE FOUND: the first-person camera settings (arm length 0) had been written to the PARENT blueprint's component
# template in memory only, so every editor restart brought back the third-person boom (400 cm behind, collision test on)
# while the body stayed hidden. Everything "felt" wrong from there (distance to objects, seeing inside props, sizes).
# This pass: camera override stored in BP_TUMCharacter itself (+ runtime guard), real convex-hull collision on props
# (GeometryScript), all invisible blocker hacks removed, walls unclimbable, soldiers back to human size, step height 45.
import unreal, importlib, inspect, traceback, random, gc
import tum_s645 as T; importlib.reload(T)
import tum_s612 as T612
import tum_graph as TG
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; CH = f"{R}/Core/BP_TUMCharacter"; EYE = 76.0
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]

# ---------------- camera ----------------
def probe():
    a = E.spawn_actor_from_class(EAL.load_asset(CH).generated_class(), V(0, 0, -20000)); r = {}
    try:
        for c in a.get_components_by_class(unreal.SpringArmComponent):
            r["arm"] = c.get_editor_property("target_arm_length"); r["coltest"] = c.get_editor_property("do_collision_test"); r["boom_z"] = c.get_editor_property("relative_location").z
        cm = a.get_component_by_class(unreal.CharacterMovementComponent); r["step"] = cm.get_editor_property("max_step_height")
    finally: E.destroy_actor(a)
    return r
def camera():
    bp = EAL.load_asset(CH)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); F = unreal.SubobjectDataBlueprintFunctionLibrary
    out = {"before": probe(), "paths": {}}
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        d = F.get_data(h); n = str(F.get_variable_name(d))
        if n not in ("CameraBoom", "FollowCamera", "Mesh"): continue
        o = None
        try: o = F.get_object_for_blueprint(d, bp)
        except Exception as e: out["gofb_err"] = str(e)[:120]
        if o is None: o = F.get_object(d)
        out["paths"][n] = o.get_path_name()
        if n == "CameraBoom":
            for k, v in (("target_arm_length", 0.0), ("relative_location", V(0, 0, EYE)), ("use_pawn_control_rotation", True), ("enable_camera_lag", False),
                         ("do_collision_test", False), ("socket_offset", V(0, 0, 0)), ("target_offset", V(0, 0, 0))): o.set_editor_property(k, v)
        if n == "FollowCamera":
            for k, v in (("use_pawn_control_rotation", False), ("field_of_view", 90.0), ("relative_location", V(0, 0, 0)), ("relative_rotation", unreal.Rotator())): o.set_editor_property(k, v)
        if n == "Mesh":
            o.set_editor_property("owner_no_see", True); o.set_editor_property("cast_hidden_shadow", True)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("use_controller_rotation_yaw", True)
    cm = cdo.get_editor_property("character_movement"); cm.set_editor_property("orient_rotation_to_movement", False); cm.set_editor_property("max_step_height", 45.0)
    BEL.compile_blueprint(bp); EAL.save_loaded_asset(bp, False)
    out["after"] = probe(); return out

def headbob():
    base = inspect.getsource(T.headbob).replace("(- 78.0", f"(- {EYE}")
    line = "(Transformation|SetRelativeLocation :self {boom}"
    assert base.count(line) == 1
    guard = base.replace(line, "(Class|SpringArmComponent|SetTargetArmLength :self {boom} :TargetArmLength 0.0)\n      " + line)
    c, k = BT.create_node, BT.connect_pins
    BT.create_node = T.SK._c; BT.connect_pins = T.SK._k; T612.TG.run = T612._run2
    try:
        for name, src in (("with_arm_guard", guard), ("plain", base)):
            try:
                ns = dict(T.__dict__); exec(src, ns); r = ns["headbob"](); return {name: str(r)[:200], "fixed_ids": dict(T612.res.get("fixed", {}))}
            except Exception: res["err"]["headbob_" + name] = traceback.format_exc()[-700:]
    finally: T612.TG.run = T612._orig_run; BT.create_node = c; BT.connect_pins = k
    return "failed"

# ---------------- collision ----------------
HULLS = {"Wooden_Crate": 1, "Wooden_Barrel": 1, "Wooden_Beam": 1, "Old_Wooden_Pole": 1, "Rope_Coil": 1, "Limestone_Slab": 2,
         "Beach_Boulder": 2, "Nordic_Beach_Boulder": 2, "Stakes": 8, "Brick_Walls": 10, "Ruins_Wall": 12, "ChurchRuin": 12, "CatapultBase": 6}
FALLBACK = {"Wooden_Crate": 0.97, "Wooden_Barrel": 0.85, "Wooden_Beam": 0.95, "Stakes": 0.8, "Old_Wooden_Pole": 0.9, "Brick_Walls": 0.9, "Ruins_Wall": 0.9,
            "ChurchRuin": 0.9, "Beach_Boulder": 0.8, "Nordic_Beach_Boulder": 0.8, "Limestone_Slab": 0.9, "CatapultBase": 0.9, "Rope_Coil": 0.85}
WALL = ("Brick_Walls", "Ruins_Wall", "ChurchRuin")
def key_of(m): return next((k for k in HULLS if k in m.get_name()), None)
def gen_hulls(m, n):
    AU = unreal.GeometryScript_AssetUtils; CO = unreal.GeometryScript_Collision
    dm = unreal.DynamicMesh(); co = unreal.GeometryScriptCopyMeshFromAssetOptions(); lod = unreal.GeometryScriptMeshReadLOD()
    try: lod.set_editor_property("lod_type", unreal.GeometryScriptLODType.RENDER_DATA); lod.set_editor_property("lod_index", 0)
    except Exception: pass
    fn = getattr(AU, "copy_mesh_from_static_mesh_v2", None) or AU.copy_mesh_from_static_mesh
    fn(m, dm, co, lod); tris = dm.get_triangle_count()
    if tris == 0:
        fn(m, dm, co, unreal.GeometryScriptMeshReadLOD()); tris = dm.get_triangle_count()
    if tris > 8000:
        for cls in ("GeometryScript_MeshSimplification", "GeometryScript_MeshSimplifyFunctions"):
            S_ = getattr(unreal, cls, None)
            if S_ and hasattr(S_, "apply_simplify_to_triangle_count"):
                try: S_.apply_simplify_to_triangle_count(dm, 6000, unreal.GeometryScriptSimplifyMeshOptions())
                except Exception: pass
                break
    if dm.get_triangle_count() > 60000: n = 1
    op = unreal.GeometryScriptCollisionFromMeshOptions()
    op.set_editor_property("method", unreal.GeometryScriptCollisionGenerationMethod.CONVEX_HULLS)
    for k, v in (("max_convex_hulls_per_mesh", n), ("emit_transaction", False), ("auto_detect_spheres", False), ("auto_detect_boxes", False), ("auto_detect_capsules", False),
                 ("simplify_hulls", True), ("convex_hull_target_face_count", 24), ("max_shape_count", 0)):
        try: op.set_editor_property(k, v)
        except Exception: pass
    CO.set_static_mesh_collision_from_mesh(dm, m, op)
    bs = m.get_editor_property("body_setup"); bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    ag = bs.get_editor_property("agg_geom"); cnt = len(ag.get_editor_property("convex_elems")) + len(ag.get_editor_property("box_elems"))
    EAL.save_loaded_asset(m, False)
    return [tris, dm.get_triangle_count(), cnt]
def sweep_ok(world, a, mesh_names):
    o, e = a.get_actor_bounds(False)
    for (s, t) in ((V(o.x - e.x - 250, o.y, o.z), V(o.x + e.x + 250, o.y, o.z)), (V(o.x, o.y - e.y - 250, o.z), V(o.x, o.y + e.y + 250, o.z)), (V(o.x, o.y, o.z + e.z + 250), V(o.x, o.y, o.z - e.z))):
        h = unreal.SystemLibrary.sphere_trace_single(world, s, t, 12.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        tp = h.to_tuple() if h else None
        if tp and tp[0] and tp[9] and isinstance(tp[9], unreal.StaticMeshActor) and tp[9].static_mesh_component.static_mesh and tp[9].static_mesh_component.static_mesh.get_name() in mesh_names: return True
    return False
def collisions():
    out = {"removed_hacks": 0, "meshes": {}, "fallback_boxes": 0, "walls_locked": 0, "wall_err": None}
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(("Blocker_", "BlockerPole_", "WallCell_", "WallTop_")): E.destroy_actor(a); out["removed_hacks"] += 1
    world = unreal.EditorLevelLibrary.get_editor_world()
    inst = {}
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor) and not a.is_hidden_ed() and a.static_mesh_component.static_mesh:
            m = a.static_mesh_component.static_mesh
            if key_of(m): inst.setdefault(m.get_name(), (m, []))[1].append(a)
    names = set(inst.keys())
    for n, (m, acts) in inst.items():
        k = key_of(m)
        try: info = gen_hulls(m, HULLS[k])
        except Exception: info = ["ERR " + traceback.format_exc()[-300:]]
        gc.collect(); unreal.SystemLibrary.collect_garbage()
        for a in acts:
            c = a.static_mesh_component; c.set_collision_profile_name("BlockAll"); a.set_actor_enable_collision(True)
        big = [a for a in acts if a.get_actor_bounds(False)[1].z * 2 > 40]
        ok = sweep_ok(world, max(big, key=lambda a: a.get_actor_bounds(False)[1].z), names) if big else None
        out["meshes"][n[:40]] = info + [len(acts), ok]
        if ok is False:
            cube = EAL.load_asset("/Engine/BasicShapes/Cube"); inv = EAL.load_asset(f"{R}/Materials/Surfaces/M_Invisible"); f = FALLBACK[k]
            for a in big:
                bb = m.get_bounding_box(); sc = a.get_actor_scale3d()
                ctr = a.get_actor_transform().transform_location(V((bb.min.x + bb.max.x) / 2, (bb.min.y + bb.max.y) / 2, (bb.min.z + bb.max.z) / 2))
                b = E.spawn_actor_from_object(cube, ctr, a.get_actor_rotation())
                b.set_actor_scale3d(V(max((bb.max.x - bb.min.x) * abs(sc.x) * f, 30) / 100, max((bb.max.y - bb.min.y) * abs(sc.y) * f, 30) / 100, (bb.max.z - bb.min.z) * abs(sc.z) / 100))
                cc = b.static_mesh_component; cc.set_material(0, inv); cc.set_collision_profile_name("BlockAll"); cc.set_cast_shadow(False); cc.set_editor_property("hidden_in_game", True)
                b.set_actor_label(f"Blocker_{out['fallback_boxes']}"); b.set_folder_path("Gameplay/Blockers"); out["fallback_boxes"] += 1
        if any(w in n for w in WALL):
            for a in acts:
                try:
                    c = a.static_mesh_component
                    c.set_editor_property("can_character_step_up_on", unreal.CanBeCharacterBase.ECB_NO)
                    ws = unreal.WalkableSlopeOverride(); ws.set_editor_property("walkable_slope_behavior", unreal.WalkableSlopeBehavior.WALKABLE_SLOPE_UNWALKABLE)
                    c.set_walkable_slope_override(ws); out["walls_locked"] += 1
                except Exception: out["wall_err"] = traceback.format_exc()[-300:]
    return out

def soldiers():
    random.seed(11); n = 0
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.SkeletalMeshActor) and not a.get_actor_label().startswith("Cavalry_"):
            m = a.skeletal_mesh_component.get_skeletal_mesh_asset()
            if m and "/War/Soldiers/" in m.get_path_name():
                s = 178.0 / 170.0 * random.uniform(0.97, 1.03); a.set_actor_scale3d(V(s, s, s)); n += 1
    return n

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("camera", camera); step("headbob", headbob)
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("collisions", collisions); step("soldiers", soldiers)
    L.save_current_level()
    res["final_probe"] = probe()
    return res
