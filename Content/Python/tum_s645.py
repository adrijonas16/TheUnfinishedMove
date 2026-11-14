# War pass 4:
# - horses never stand still: at the end of a charge (or after waiting too long without a clear line) they vanish and
#   reappear at a random spot 30-42 m from you, inside the field, and charge again
# - knockdown no longer locks your controls; camera dips and recovers in ~0.7 s
# - corpses / fallen skirmish soldiers sit on the ground (offset measured from the death pose)
# - wooden props: simple collision boxes removed so the real shape is used
# - head bob: the view dips with each footstep and sways slightly, scaled by speed (sprint = stronger)
import unreal, importlib, traceback, math, re, random, gc
import tum_s641 as P; importlib.reload(P)
import tum_s623 as SK; importlib.reload(SK)
import tum_graph as TG
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SMS = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"; H = P.H; S = P.S
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
G = lambda n: f"(Variables|Default|Get{n})"
def teleport(tag):
    return (f"(bind tpa{tag} (Math|Random|RandomFloatinRange :Min 0.0 :Max 6.283))\n"
            f"      (bind tpr{tag} (Math|Random|RandomFloatinRange :Min 3000.0 :Max 4200.0))\n"
            f"      (Transformation|SetActorLocation :NewLocation (Math|Vector|MakeVector (Math|Float|Clamp(Float) (+ (.x pl) (* (Math|Trig|Cos(Radians) tpa{tag}) tpr{tag})) -600.0 9800.0) "
            f"(Math|Float|Clamp(Float) (+ (.y pl) (* (Math|Trig|Sin(Radians) tpa{tag}) tpr{tag})) -4200.0 4200.0) (.z me)) :bTeleport true)")

def cav_transform(code):
    old_wait = "(Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 2.5 :Max 5.5))"
    if code.count(old_wait) != 1: raise RuntimeError("stop wait count %d" % code.count(old_wait))
    code = code.replace(old_wait, "(Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 0.8 :Max 2.0))\n      " + teleport("a"))
    dec = "(Variables|Default|SetWait (- (Variables|Default|GetWait) DeltaSeconds))"
    if code.count(dec) != 1: raise RuntimeError("dec count %d" % code.count(dec))
    code = code.replace(dec, dec + f"\n    (if (< {G('Wait')} -3.0)\n      " + teleport("b") + "\n      (Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 0.5 :Max 1.5)))")
    # knockdown: keep the camera dip, drop the input lock, shorter
    for tag in ("(Input|DisableInput", "(Input|EnableInput"):
        i = code.find(tag)
        while i >= 0:
            e = H.expr_at(code, i); code = code[:i] + code[i + len(e):]; i = code.find(tag)
    code = code.replace("(Utilities|FlowControl|Delay 1.2)", "(Utilities|FlowControl|Delay 0.25)").replace("(Utilities|FlowControl|Delay 0.06)", "(Utilities|FlowControl|Delay 0.035)")
    return code
_h2 = P.hoist2
def hoist3(code):
    code, n = _h2(code)
    if "GetRun) 7500.0" in code: code = cav_transform(code); res["cav_transform"] = True
    return code, n
def horses():
    TG.ensure_vars(f"{WB}/BP_Cavalry", [("Bumps", "int")])
    H.hoist = hoist3
    from editor_toolset.toolsets import blueprint_dsl
    blueprint_dsl.Transpiler.transpile = H.wrapped
    try: return H.C632.run()
    finally: blueprint_dsl.Transpiler.transpile = H.TRUE_ORIG; H.hoist = P._old_hoist

# ---------------- death pose offset ----------------
def death_drop():
    Pz = unreal.AnimPoseExtensions; opts = unreal.AnimPoseEvaluationOptions()
    a = S.A("dying_backwards"); L_ = a.get_play_length()
    pose = Pz.get_anim_pose_at_time(a, L_ - 0.01, opts)
    zs = []
    for b in Pz.get_bone_names(pose):
        bn = str(b)
        if bn.endswith("_end") or bn in ("SmartRigArmature",): continue
        zs.append(Pz.get_bone_pose(pose, bn, unreal.AnimPoseSpaces.WORLD).translation.z)
    return min(zs)

def skirmish_bp(drop):
    src = __import__("inspect").getsource(SK.skirmish_bp)
    old = "      {play('B', g('DieAnim'), 'false')}\n"
    assert src.count(old) == 1
    src = src.replace(old, old + "      (Variables|Default|SetDropT 0.0)\n")
    # sink the fallen body gradually over the fall so it ends lying on the ground
    st3 = "  (if (== {g('State')} 3)\n"
    assert src.count(st3) == 1
    src = src.replace(st3, st3 + "    (if (< {g('DropT')} 1.0)\n      (Variables|Default|SetDropT (+ {g('DropT')} (/ DeltaSeconds 2.0)))\n      (Transformation|SetActorLocation :self {g('B')} :NewLocation (Math|Vector|MakeVector (.x lb) (.y lb) (- (.z lb) (* (/ DeltaSeconds 2.0) {g('Drop')}))) :bTeleport true))\n")
    src = src.replace('[("State", "int")] + [(n, "float") for n in ("T", "Dur", "Speed", "EX", "EY", "ClangT", "Wake")]',
                      '[("State", "int")] + [(n, "float") for n in ("T", "Dur", "Speed", "EX", "EY", "ClangT", "Wake", "DropT", "Drop")]')
    src = src.replace('"Clang", "Speed", "Wake"], {"Speed": 490.0, "Wake": 4500.0}', '"Clang", "Speed", "Wake", "Drop"], {"Speed": 490.0, "Wake": 4500.0, "Drop": %f}' % drop)
    ns = dict(SK.__dict__); exec(src, ns)
    BT.create_node = SK._c; BT.connect_pins = SK._k
    try: return ns["skirmish_bp"]()
    finally: BT.create_node = SK._OC; BT.connect_pins = SK._OK

def bodies_and_wood(minz):
    out = {"minz": round(minz, 1), "corpses": 0, "drop_set": 0, "wood": []}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("Corpse_") and isinstance(a, unreal.SkeletalMeshActor):
            s = a.get_actor_scale3d().z; l = a.get_actor_location()
            a.set_actor_location(V(l.x, l.y, 2.0 - (minz - 6.0) * s), False, False); out["corpses"] += 1
        if a.get_class().get_name() == "BP_Skirmish_C":
            b = a.get_editor_property("B"); s = b.get_actor_scale3d().z if b else 1.0
            a.set_editor_property("Drop", max(0.0, (minz - 6.0) * s)); out["drop_set"] += 1
    done = set()
    for a in E.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor): continue
        m = a.static_mesh_component.static_mesh
        if not m or m.get_name() in done: continue
        if any(k in m.get_name() for k in P.WOOD):
            n0 = SMS.get_simple_collision_count(m)
            SMS.remove_collisions(m)
            m.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            EAL.save_loaded_asset(m, False); done.add(m.get_name()); out["wood"].append([m.get_name(), n0])
    return out

# ---------------- head bob ----------------
def headbob():
    p = S.bp("BP_HeadBob")
    TG.ensure_vars(p, [("Ph", "float"), ("Amp", "float"), ("BaseZ", "float"), ("bInit", "bool")])
    boom = "(Class|BPThirdPersonCharacter|GetCameraBoom :self ch)"
    code = f"""
(event EventTick (DeltaSeconds)
  (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object (Game|GetPlayerCharacter 0))
    (:then
      (bind v (Transformation|GetVelocity :self ch))
      (bind sp (Math|Vector|VectorLength (Math|Vector|MakeVector (.x v) (.y v) 0.0)))
      (bind k (Math|Float|Clamp(Float) (/ sp 520.0) 0.0 1.6))
      (Variables|Default|SetAmp (Math|Interpolation|FInterpTo :Current {G('Amp')} :Target (select (Class|CharacterMovementComponent|IsMovingOnGround :self (Class|Character|GetCharacterMovement :self ch)) k 0.0) :DeltaTime DeltaSeconds :InterpSpeed 8.0))
      (Variables|Default|SetPh (+ {G('Ph')} (* DeltaSeconds (* (/ sp 175.0) 3.1416))))
      (bind sn (Math|Trig|Sin(Radians) {G('Ph')}))
      (Transformation|SetRelativeLocation :self {boom} :NewLocation (Math|Vector|MakeVector 0.0 (* (* sn 1.4) {G('Amp')}) (- 78.0 (* (* (* sn sn) 3.6) {G('Amp')})))))
    (:CastFailed)))
"""
    r = TG.run(p, code, clear=True); return str(r)[:300]
def place_bob(maps):
    cls = EAL.load_asset(f"{WB}/BP_HeadBob").generated_class(); out = []
    for mp in maps:
        L.load_level(f"{R}/Maps/{mp}")
        for a in list(E.get_all_level_actors()):
            if a.get_actor_label() == "HeadBob": E.destroy_actor(a)
        h = E.spawn_actor_from_class(cls, V(0, 0, -5000)); h.set_actor_label("HeadBob"); h.set_folder_path("Gameplay")
        L.save_current_level(); out.append(mp)
    return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("horses", horses)
    minz = None
    try: minz = death_drop(); res["death_minz"] = minz
    except Exception: res["err"]["death"] = traceback.format_exc()[-800:]
    if minz is not None: step("skirmish_bp", lambda: skirmish_bp(max(0.0, minz - 6.0) * 1.09))
    BT_c, BT_k = BT.create_node, BT.connect_pins
    BT.create_node = SK._c; BT.connect_pins = SK._k
    import tum_s612 as T612
    T612.TG.run = T612._run2
    try: step("headbob", headbob)
    finally: T612.TG.run = T612._orig_run; BT.create_node = BT_c; BT.connect_pins = BT_k
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    if minz is not None: step("bodies_and_wood", lambda: bodies_and_wood(minz))
    L.save_current_level()
    if "headbob" in res["ok"]: step("place_bob", lambda: place_bob(["M_Cut_WarField", "M_FactoryHub"]))
    return res

def fix_bodies():
    out = {"corpses": 0, "drop": 0}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("Corpse_") and isinstance(a, unreal.SkeletalMeshActor):
            l = a.get_actor_location(); a.set_actor_location(V(l.x, l.y, -6.0), False, False); out["corpses"] += 1
        if a.get_class().get_name() == "BP_Skirmish_C":
            b = a.get_editor_property("B"); s = b.get_actor_scale3d().z if b else 1.0
            a.set_editor_property("Drop", 8.0 * s); out["drop"] += 1
    return out
def run2():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    import tum_s612 as T612
    BT_c, BT_k = BT.create_node, BT.connect_pins
    BT.create_node = SK._c; BT.connect_pins = SK._k; T612.TG.run = T612._run2
    try: step("headbob", headbob)
    finally: T612.TG.run = T612._orig_run; BT.create_node = BT_c; BT.connect_pins = BT_k
    L.load_level(f"{R}/Maps/M_Cut_WarField"); step("fix_bodies", fix_bodies); L.save_current_level()
    if "headbob" in res["ok"]: step("place_bob", lambda: place_bob(["M_Cut_WarField", "M_FactoryHub"]))
    return res
