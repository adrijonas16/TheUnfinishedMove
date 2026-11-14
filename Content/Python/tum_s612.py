# Progress pass: no sword outside War, silver seal in hand back in the factory, factory spawn per stage,
# goal beacon + seal shown at the War goal, scenery behind the War start, horses stop at walls.
import unreal, importlib, traceback, inspect, re
import tum_s580 as C; importlib.reload(C)
import tum_s590 as FP; importlib.reload(FP)
import tum_s610 as X; importlib.reload(X)
import tum_graph as TG
from editor_toolset.toolsets.blueprint import BlueprintTools as BT, _BlueprintCache
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; MEL = unreal.MaterialEditingLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; CH = "/Game/TUM/Core/BP_TUMCharacter"
GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
res = {"ok": [], "err": {}, "fixed": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]

# ---- resolve node ids that are spelled with the wrong category ----
_orig_run = TG.run
def _resolve(bp_path, code):
    bp = EAL.load_asset(bp_path); _BlueprintCache.invalidate(bp); graph = BEL.find_event_graph(bp)
    for m in TG.check_ids(graph, code):
        short = m.split("|")[-1]
        try: cands = [c for c in BT.find_node_types(graph, short) if c.split("|")[-1].lower() == short.lower()]
        except Exception: cands = []
        if cands:
            code = code.replace("(" + m + " ", "(" + cands[0] + " ").replace("(" + m + ")", "(" + cands[0] + ")"); res["fixed"][m] = cands[0]
    return code
def _run2(bp_path, code, *a, **k): return _orig_run(bp_path, _resolve(bp_path, code), *a, **k)

def seal_mesh():
    for p in EAL.list_assets(f"{R}/Props/Seal", recursive=True, include_folder=False):
        a = EAL.load_asset(p.split(".")[0])
        if isinstance(a, unreal.StaticMesh): return a
    raise RuntimeError("no seal mesh")

def g(n): return f"(Variables|Default|Get{n})"

# ---- character: seal component + BeginPlay (sword only in War, seal in factory after War, stage spawn) ----
def character():
    bp = EAL.load_asset(CH)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); F = unreal.SubobjectDataBlueprintFunctionLibrary
    hs = {str(F.get_variable_name(F.get_data(h))): h for h in sds.k2_gather_subobject_data_for_blueprint(bp)}
    if "Seal" not in hs:
        p = unreal.AddNewSubobjectParams(parent_handle=hs["CapsuleComponent"], new_class=unreal.StaticMeshComponent, blueprint_context=bp)
        nh, fail = sds.add_new_subobject(p); sds.rename_subobject(nh, unreal.Text("Seal")); hs["Seal"] = nh
    comp = F.get_object(F.get_data(hs["Seal"])); m = seal_mesh(); comp.set_editor_property("static_mesh", m)
    bb = m.get_bounding_box(); ext = max(bb.max.x - bb.min.x, bb.max.y - bb.min.y, bb.max.z - bb.min.z, 0.01); s = 13.0 / ext
    comp.set_editor_property("relative_scale3d", V(s, s, s))
    comp.set_collision_profile_name("NoCollision"); comp.set_editor_property("cast_shadow", False); comp.set_editor_property("visible", False)
    BEL.compile_blueprint(bp); EAL.save_loaded_asset(bp, False)
    b = EAL.load_asset(CH); _BlueprintCache.invalidate(b); gr = BEL.find_event_graph(b)
    for n in list(BT.find_nodes(gr)):
        t = BT._get_node_info(n).type_id
        if t in ("AddEvent|EventBeginPlay", "Transformation|AttachComponentToComponent", "Transformation|SetRelativeRotation", "Transformation|SetRelativeLocation"): BT.delete_node(n)
    _BlueprintCache.invalidate(b)
    sl, sr = FP.SWORD_LOC, FP.SWORD_ROT
    cam = "(Variables|Camera|GetFollowCamera)"
    def vis(c, v): return f"(Rendering|SetVisibility :self {g(c)} :bNewVisibility {v} :bPropagateToChildren false)"
    def spawn(n): return f"""      (for s{n} (Actor|GetAllActorswithTag :Tag "SpawnS{n}")
        (Transformation|SetActorLocationAndRotation :NewLocation (Transformation|GetActorLocation :self s{n}) :NewRotation (Transformation|GetActorRotation :self s{n}) :bTeleport true)
        (Pawn|SetControlRotation :self (Game|GetPlayerController 0) :NewRotation (Transformation|GetActorRotation :self s{n})))"""
    code = f"""
(event EventBeginPlay
  (Transformation|AttachComponentToComponent :self {g('Sword')} :Parent {cam} :SocketName "None" :LocationRule "SnapToTarget" :RotationRule "SnapToTarget" :ScaleRule "KeepWorld" :bWeldSimulatedBodies false)
  (Transformation|SetRelativeRotation :self {g('Sword')} :NewRotation (Math|Rotator|MakeRotator :Roll {sr[0]} :Pitch {sr[1]} :Yaw {sr[2]}))
  (Transformation|SetRelativeLocation :self {g('Sword')} :NewLocation (Math|Vector|MakeVector {sl[0]} {sl[1]} {sl[2]}))
  {vis('Sword', 'false')}
  (Transformation|AttachComponentToComponent :self {g('Seal')} :Parent {cam} :SocketName "None" :LocationRule "SnapToTarget" :RotationRule "SnapToTarget" :ScaleRule "KeepWorld" :bWeldSimulatedBodies false)
  (Transformation|SetRelativeRotation :self {g('Seal')} :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 15.0 :Yaw 160.0))
  (Transformation|SetRelativeLocation :self {g('Seal')} :NewLocation (Math|Vector|MakeVector 42.0 -17.0 -15.0))
  {vis('Seal', 'false')}
  (for r (Actor|GetAllActorswithTag :Tag "RainOn")
    {vis('Rain', 'true')}
    {vis('Sword', 'true')})
  (CallFunction|Progress))

(event Custom|Progress
  (bind gi {GP}
    (:then
      (if (and (Class|BPGameProgress|GetDragonDone :self gi) (not (Class|BPGameProgress|GetWarDone :self gi)))
{spawn(1)})
      (if (and (Class|BPGameProgress|GetWarDone :self gi) (not (Class|BPGameProgress|GetCliffDone :self gi)))
{spawn(2)})
      (if (Class|BPGameProgress|GetCliffDone :self gi)
{spawn(3)})
      (if (Class|BPGameProgress|GetWarDone :self gi)
        (for so (Actor|GetAllActorswithTag :Tag "SealOn")
          {vis('Seal', 'true')})))
    (:CastFailed)))
"""
    return str(TG.run(CH, code, events=["Progress"], clear=False))[:300]

# ---- cavalry: two-height wall trace while charging + only charge with a clear line to the player ----
def cavalry():
    src = inspect.getsource(C.cavalry_bp)
    a = src.index("(event Custom|KnockDown"); b = src.index("(event EventTick (DeltaSeconds)")
    fp = inspect.getsource(FP.cavalry)
    knock = fp[fp.index('new = f"""') + 10: fp.index('"""\n    src = src[:old_start]')]
    cam = "(Class|BPThirdPersonCharacter|GetFollowCamera :self ch)"
    down = "\n".join(f"      (Transformation|SetRelativeLocationAndRotation :self {cam} :NewLocation (Math|Vector|MakeVector 0.0 0.0 {-22.0 * k}) :NewRotation (Math|Rotator|MakeRotator :Roll {13.0 * k} :Pitch {7.0 * k} :Yaw 0.0))\n      (Utilities|FlowControl|Delay 0.03)" for k in range(1, 7))
    up = "\n".join(f"      (Transformation|SetRelativeLocationAndRotation :self {cam} :NewLocation (Math|Vector|MakeVector 0.0 0.0 {-22.0 * k}) :NewRotation (Math|Rotator|MakeRotator :Roll {13.0 * k} :Pitch {7.0 * k} :Yaw 0.0))\n      (Utilities|FlowControl|Delay 0.06)" for k in range(5, -1, -1))
    knock = knock.replace("{down}", down).replace("{up}", up).replace("{{PL}}", "{PL}")
    src = src[:a] + knock + src[b:]
    tr_line = re.search(r"\n(\s+)trace = f\".*\"\n", src)
    ind = tr_line.group(1)
    new_tr = (f"\n{ind}def _tr(h): return f\"(Collision|LineTraceByChannel :Start (Math|Vector|MakeVector (+ (.x me) (* {{g('DX')}} 150.0)) (+ (.y me) (* {{g('DY')}} 150.0)) (+ (.z me) {{h}})) :End (Math|Vector|MakeVector (+ (.x me) (* {{g('DX')}} 560.0)) (+ (.y me) (* {{g('DY')}} 560.0)) (+ (.z me) {{h}})))\"\n"
              f"{ind}trace = f\"(or {{_tr(60.0)}} {{_tr(170.0)}})\"\n"
              f"{ind}los = \"(Collision|LineTraceByChannel :Start (Math|Vector|MakeVector (+ (.x me) (* (/ dpx (+ dp 1.0)) 150.0)) (+ (.y me) (* (/ dpy (+ dp 1.0)) 150.0)) (+ (.z me) 130.0)) :End (Math|Vector|MakeVector (- (.x pl) (* (/ dpx (+ dp 1.0)) 160.0)) (- (.y pl) (* (/ dpy (+ dp 1.0)) 160.0)) (+ (.z pl) 40.0)))\"\n")
    src = src[:tr_line.start()] + new_tr + src[tr_line.end():]
    old = "(if (and (< {g('Wait')} 0.0) (< dp 4800.0))"
    if old not in src: raise RuntimeError("charge condition not found")
    src = src.replace(old, "(if (and (and (< {g('Wait')} 0.0) (< dp 4800.0)) (not {los}))")
    ns = dict(C.__dict__); exec(src, ns); return ns["cavalry_bp"]()

# ---- War level: beacon + seal at the goal, scenery behind the start ----
def beacon_material():
    p = f"{R}/Materials/M_GoalBeacon"
    if EAL.does_asset_exist(p): return EAL.load_asset(p)
    m = AT.create_asset("M_GoalBeacon", f"{R}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE); m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    try: m.set_editor_property("use_translucency_vertex_fog", False)
    except Exception: pass
    c = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -600, -100); c.set_editor_property("constant", unreal.LinearColor(1.0, 0.55, 0.15, 1))
    fr = MEL.create_material_expression(m, unreal.MaterialExpressionFresnel, -700, 100); fr.set_editor_property("exponent", 1.5)
    one = MEL.create_material_expression(m, unreal.MaterialExpressionOneMinus, -500, 100); MEL.connect_material_expressions(fr, "", one, "")
    mu = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 0); MEL.connect_material_expressions(c, "", mu, "A"); MEL.connect_material_expressions(one, "", mu, "B")
    k = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -150, 0); k.set_editor_property("const_b", 2.5); MEL.connect_material_expressions(mu, "", k, "A")
    MEL.connect_material_property(k, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m

def war():
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    out = {}
    acts = list(E.get_all_level_actors())
    for a in acts:
        if a.get_actor_label().startswith(("Goal_Beacon", "Goal_Seal", "Goal_BeaconLight", "Behind_")): E.destroy_actor(a)
    acts = list(E.get_all_level_actors())
    goals = [a for a in acts if a.get_actor_label().startswith("Goal_War")]
    gl = min(goals, key=lambda a: len(a.get_actor_label())).get_actor_location() if goals else None
    out["goal"] = str(gl)
    if gl:
        mat = beacon_material()
        bc = E.spawn_actor_from_object(EAL.load_asset("/Engine/BasicShapes/Cylinder"), V(gl.x, gl.y, gl.z + 2500), unreal.Rotator())
        bc.set_actor_scale3d(V(0.9, 0.9, 50)); bc.static_mesh_component.set_material(0, mat)
        bc.static_mesh_component.set_collision_profile_name("NoCollision"); bc.static_mesh_component.set_cast_shadow(False)
        bc.set_actor_label("Goal_Beacon"); bc.set_folder_path("Gameplay/Goal")
        lt = E.spawn_actor_from_class(unreal.PointLight, V(gl.x, gl.y, gl.z + 350), unreal.Rotator())
        pc = lt.point_light_component; pc.set_intensity(12000.0); pc.set_attenuation_radius(2500.0); pc.set_light_color(unreal.LinearColor(1.0, 0.6, 0.25, 1)); pc.set_cast_shadows(False)
        lt.set_actor_label("Goal_BeaconLight"); lt.set_folder_path("Gameplay/Goal")
        m = seal_mesh(); bb = m.get_bounding_box(); ext = max(bb.max.z - bb.min.z, 0.01); s = 90.0 / ext
        se = E.spawn_actor_from_object(m, V(gl.x, gl.y, gl.z + 170 - bb.min.z * s), unreal.Rotator(roll=0, pitch=0, yaw=30))
        se.set_actor_scale3d(V(s, s, s)); se.static_mesh_component.set_collision_profile_name("NoCollision")
        se.set_actor_label("Goal_Seal"); se.set_folder_path("Gameplay/Goal")
    # scenery behind the start: copy the first strip of battle behind the back wall
    ps = [a for a in acts if isinstance(a, unreal.PlayerStart)]
    sx = ps[0].get_actor_location().x if ps else 0.0
    out["start_x"] = sx
    skip = ("Goal", "CP_", "Bound", "Catapult", "Cavalry", "Archer", "Crater", "RainOn", "ObjHUD", "HUD", "Knight", "Guide", "Hint", "Torch_Light_Main", "Sky", "Sun", "Fog", "PostProcess", "Player", "Mini", "GroundSmoke")
    keep_cls = (unreal.StaticMeshActor, unreal.SkeletalMeshActor, unreal.PointLight, unreal.NiagaraActor)
    band = [a for a in acts if isinstance(a, keep_cls) and not a.get_actor_label().startswith(skip)
            and sx + 300 < a.get_actor_location().x < sx + 3300 and abs(a.get_actor_location().y) < 4600 and not a.is_hidden_ed()]
    out["band"] = len(band)
    world = unreal.EditorLevelLibrary.get_editor_world()
    dup = E.duplicate_actors(band, world, V(-3900, 0, 0))
    for i, d in enumerate(dup):
        d.set_actor_label(f"Behind_{i}"); d.set_folder_path("Art/War/Behind")
    # ground smoke behind too
    sm = [a for a in acts if a.get_actor_label().startswith("GroundSmoke_")][:4]
    for i, d in enumerate(E.duplicate_actors(sm, world, V(0, 0, 0))):
        l = d.get_actor_location(); d.set_actor_location(V(sx - 1200 - 900 * i, l.y, l.z), False, False); d.set_actor_label(f"Behind_Smoke{i}"); d.set_folder_path("Art/War/Behind")
    out["dup"] = len(dup)
    L.save_current_level(); return out

# ---- Factory: stage spawn points + SealOn marker ----
def floor_z(world, x, y, z0):
    try:
        h = unreal.SystemLibrary.line_trace_single(world, V(x, y, z0 + 160), V(x, y, z0 - 260), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h:
            t = h.to_tuple()
            if t[0]: return t[4].z
    except Exception: pass
    return z0
def factory():
    L.load_level(f"{R}/Maps/M_FactoryHub")
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(("SpawnS", "SealOn_Marker")): E.destroy_actor(a)
    world = unreal.EditorLevelLibrary.get_editor_world(); out = {}
    for n, (x, y, z, yaw) in {1: (4520, -553, 302, 0.0), 2: (5500, -575, 324, 0.0), 3: (6400, 0, 0, 0.0)}.items():
        fz = floor_z(world, x, y, z)
        tp = E.spawn_actor_from_class(unreal.TargetPoint, V(x, y, fz + 100), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
        tp.tags = [unreal.Name(f"SpawnS{n}")]; tp.set_actor_label(f"SpawnS{n}"); tp.set_folder_path("Gameplay/Spawn"); out[n] = fz
    tp = E.spawn_actor_from_class(unreal.TargetPoint, V(0, 0, -9000)); tp.tags = [unreal.Name("SealOn")]; tp.set_actor_label("SealOn_Marker"); tp.set_folder_path("Gameplay/Spawn")
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    TG.run = _run2
    try:
        step("war", war); step("factory", factory)
        step("character", character); step("cavalry", cavalry)
        step("hud", X.hud_bp)
    finally:
        TG.run = _orig_run
    return res

def run_hud():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    TG.run = _run2
    try: step("hud", X.hud_bp)
    finally: TG.run = _orig_run
    return res
