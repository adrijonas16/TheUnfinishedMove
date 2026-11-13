# War, medieval pass: Meshy soldiers (3 looks, one skeleton), scattered wanderers that run between cover and hide,
# sword duels, knights that chase (Cut Boost knocks them down), catapults throwing stones (no gunpowder)
import unreal, importlib, traceback, math, random
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"; AN = f"{WB}/Soldiers/Anim/soldier3"
SK = unreal.SkeletalMeshActor.static_class(); AS = unreal.AnimSequence.static_class(); SB = unreal.SoundBase.static_class()
MESHES = [f"{WB}/Soldiers/M1/soldier1", f"{WB}/Soldiers/M2/soldier2", f"{WB}/Soldiers/Anim/soldier3"]
SWORD = "/Game/MS/3D/Sword_uitlbiaga/SM_Sword_uitlbiaga_00_N1"
ROCK = f"{R}/Props/PolyHaven/boulder_01/boulder_01/StaticMeshes/boulder_01"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
def A(n): return EAL.load_asset(AN + n)
def bp(name):
    p = f"{WB}/{name}"
    if not EAL.does_asset_exist(p): BT.create(WB, name, unreal.Actor.static_class())
    return p
def editable(p, names, defaults={}):
    b = EAL.load_asset(p)
    for n in names: BEL.set_blueprint_variable_instance_editable(b, n, True)
    BEL.compile_blueprint(b); cdo = unreal.get_default_object(b.generated_class())
    for k, v in defaults.items(): cdo.set_editor_property(k, v)
    EAL.save_loaded_asset(b, False)
def mesh(var): return f"(Class|SkeletalMeshActor|GetSkeletalMeshComponent :self {g(var)})"
def play(var, anim, loop="true"): return f"(Components|Animation|PlayAnimation :self {mesh(var)} :NewAnimToPlay {anim} :bLooping {loop})"

def sounds():
    tasks = []
    for f in ("SFX_StoneImpact", "SFX_CatapultLaunch"):
        t = unreal.AssetImportTask(); t.set_editor_property("filename", rf"C:\UnrealProjects\TheUnfinishedMove\SourceArt\audio\sfx\{f}.wav")
        t.set_editor_property("destination_path", f"{R}/Audio/SFX"); t.set_editor_property("automated", True); t.set_editor_property("save", True); t.set_editor_property("replace_existing", True)
        tasks.append(t)
    AT.import_asset_tasks(tasks); return "ok"

def wanderer():
    p = bp("BP_Wanderer")
    TG.ensure_vars(p, [(n, "float") for n in ("AX", "AY", "BX", "BY", "CX", "CY", "TX", "TY", "Speed", "Wait")] + [("Idx", "int")],
                   objs=[("Body", SK), ("RunAnim", AS), ("HideAnim", AS)])
    code = f"""
(event EventBeginPlay
  (Variables|Default|SetIdx 1)
  (Variables|Default|SetWait 0.0))

(event EventTick (DeltaSeconds)
  (if (> {g('Wait')} 0.0)
    (Variables|Default|SetWait (- {g('Wait')} DeltaSeconds))
    (if (< {g('Wait')} 0.0) {play('Body', g('RunAnim'))})
    (else
      (if (== {g('Idx')} 0) (Variables|Default|SetTX {g('AX')}) (Variables|Default|SetTY {g('AY')}))
      (if (== {g('Idx')} 1) (Variables|Default|SetTX {g('BX')}) (Variables|Default|SetTY {g('BY')}))
      (if (== {g('Idx')} 2) (Variables|Default|SetTX {g('CX')}) (Variables|Default|SetTY {g('CY')}))
      (bind me (Transformation|GetActorLocation))
      (bind dx (- {g('TX')} (.x me)))
      (bind dy (- {g('TY')} (.y me)))
      (bind dist (Math|Vector|VectorLength (Math|Vector|MakeVector dx dy 0.0)))
      (if (< dist 40.0)
        (if (== {g('Idx')} 2) (Variables|Default|SetIdx 0) (else (Variables|Default|SetIdx (+ {g('Idx')} 1))))
        (Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 1.5 :Max 5.0))
        {play('Body', g('HideAnim'))}
        (else
          (bind k (/ (* {g('Speed')} DeltaSeconds) dist))
          (Transformation|SetActorLocation :NewLocation (Math|Vector|MakeVector (+ (.x me) (* dx k)) (+ (.y me) (* dy k)) (.z me)) :bTeleport true)
          (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start me :Target (Math|Vector|MakeVector {g('TX')} {g('TY')} (.z me))) :bTeleportPhysics true))))))
"""
    r = TG.run(p, code, clear=True)
    editable(p, ["AX", "AY", "BX", "BY", "CX", "CY", "Speed", "Body", "RunAnim", "HideAnim"], {"Speed": 380.0}); return str(r)[:200]

def knight():
    p = bp("BP_Knight")
    TG.ensure_vars(p, [("State", "int"), ("HomeX", "float"), ("HomeY", "float"), ("Chase", "float"), ("Speed", "float"), ("Sight", "float")],
                   objs=[("Body", SK), ("RunAnim", AS), ("IdleAnim", AS), ("HitAnim", AS), ("DieAnim", AS), ("Shout", SB), ("Clang", SB)])
    PUSH = ("(Character|LaunchCharacter :self ch :LaunchVelocity (Math|Vector|MakeVector (* (- (.x pp) (.x me)) 3.0) (* (- (.y pp) (.y me)) 3.0) 250.0) :bXYOverride true :bZOverride true)")
    code = f"""
(event EventBeginPlay
  (bind l (Transformation|GetActorLocation))
  (Variables|Default|SetHomeX (.x l))
  (Variables|Default|SetHomeY (.y l))
  (Variables|Default|SetState 0))

(event EventTick (DeltaSeconds)
  (bind me (Transformation|GetActorLocation))
  (bind pp (Transformation|GetActorLocation :self {PL}))
  (bind d (Transformation|GetDistanceTo :OtherActor {PL}))
  (bind open (and (> (.y pp) -790.0) (< (.y pp) 790.0)))
  (if (== {g('State')} 0)
    (if (and open (< d {g('Sight')}))
      (Variables|Default|SetState 1)
      (Variables|Default|SetChase 0.0)
      {play('Body', g('RunAnim'))}
      (Audio|PlaySoundatLocation :Sound {g('Shout')} :Location me :VolumeMultiplier 0.9)))
  (if (== {g('State')} 1)
    (Variables|Default|SetChase (+ {g('Chase')} DeltaSeconds))
    (bind tgt (Math|Vector|MakeVector (.x pp) (.y pp) (.z me)))
    (bind dir (Math|Vector|GetForwardVector :InRot (Math|Rotator|FindLookatRotation :Start me :Target tgt)))
    (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterptoConstant :Current me :Target tgt :DeltaTime DeltaSeconds :InterpSpeed {g('Speed')}) :bTeleport true)
    (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start me :Target tgt) :bTeleportPhysics true)
    (if (Collision|LineTraceByChannel :Start (Math|Vector|MakeVector (+ (.x me) (* (.x dir) 40.0)) (+ (.y me) (* (.y dir) 40.0)) (+ (.z me) 90.0)) :End (Math|Vector|MakeVector (+ (.x me) (* (.x dir) 150.0)) (+ (.y me) (* (.y dir) 150.0)) (+ (.z me) 90.0)))
      (if (> d 220.0) (Variables|Default|SetState 2) (Variables|Default|SetChase 0.0)))
    (if (< d 170.0)
      (if (> (Math|Vector|VectorLength (Math|Vector|MakeVector (.x (Transformation|GetVelocity :self {PL})) (.y (Transformation|GetVelocity :self {PL})) 0.0)) 700.0)
        (Variables|Default|SetState 3)
        {play('Body', g('DieAnim'), 'false')}
        (Audio|PlaySoundatLocation :Sound {g('Clang')} :Location me :VolumeMultiplier 1.0 :PitchMultiplier 0.8)
        (else
          (Variables|Default|SetState 2)
          (Variables|Default|SetChase -0.9)
          {play('Body', g('HitAnim'), 'false')}
          (Audio|PlaySoundatLocation :Sound {g('Clang')} :Location me :VolumeMultiplier 0.8)
          (bind ch (Utilities|Casting|CastToCharacter :Object {PL})
            (:then {PUSH})
            (:CastFailed))))
      (else
        (if (or (not open) (> {g('Chase')} 7.0))
          (Variables|Default|SetState 2)
          (Variables|Default|SetChase 0.0)))))
  (if (== {g('State')} 2)
    (if (< {g('Chase')} 0.0)
      (Variables|Default|SetChase (+ {g('Chase')} DeltaSeconds))
      (if (not (< {g('Chase')} 0.0)) {play('Body', g('RunAnim'))})
      (else
        (bind home (Math|Vector|MakeVector {g('HomeX')} {g('HomeY')} (.z me)))
        (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterptoConstant :Current me :Target home :DeltaTime DeltaSeconds :InterpSpeed 260.0) :bTeleport true)
        (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start me :Target home) :bTeleportPhysics true)
        (if (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x me) {g('HomeX')}) (- (.y me) {g('HomeY')}) 0.0)) 20.0)
          (Variables|Default|SetState 0)
          {play('Body', g('IdleAnim'))})))))
"""
    r = TG.run(p, code, clear=True)
    editable(p, ["Body", "RunAnim", "IdleAnim", "HitAnim", "DieAnim", "Shout", "Clang", "Speed", "Sight"], {"Speed": 340.0, "Sight": 760.0}); return str(r)[:300]

def catapult_bp():
    p = bp("BP_Catapult")
    TG.ensure_vars(p, [(n, "float") for n in ("T", "Next", "OX", "OY", "OZ", "TX", "TY", "TZ")] + [("Fly", "bool")],
                   objs=[("Rock", unreal.StaticMeshActor.static_class()), ("Launch", SB), ("Impact", SB), ("Dust", unreal.NiagaraSystem.static_class())])
    code = f"""
(event EventTick (DeltaSeconds)
  (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
  (if {g('Fly')}
    (bind a (/ {g('T')} 1.9))
    (bind h (* (Math|Trig|Sin(Radians) (* a 3.14159)) 2200.0))
    (Transformation|SetActorLocation :self {g('Rock')} :NewLocation (Math|Vector|MakeVector (+ {g('OX')} (* (- {g('TX')} {g('OX')}) a)) (+ {g('OY')} (* (- {g('TY')} {g('OY')}) a)) (+ (+ {g('OZ')} (* (- {g('TZ')} {g('OZ')}) a)) h)) :bTeleport true)
    (if (> a 1.0)
      (Variables|Default|SetFly false)
      (Variables|Default|SetT 0.0)
      (Variables|Default|SetNext (Math|Random|RandomFloatinRange :Min 3.5 :Max 7.0))
      (bind tg (Math|Vector|MakeVector {g('TX')} {g('TY')} {g('TZ')}))
      (Transformation|SetActorLocation :self {g('Rock')} :NewLocation tg :bTeleport true)
      (Audio|PlaySoundatLocation :Sound {g('Impact')} :Location tg :VolumeMultiplier 1.3 :PitchMultiplier (Math|Random|RandomFloatinRange :Min 0.85 :Max 1.1))
      (Niagara|SpawnSystematLocation :SystemTemplate {g('Dust')} :Location tg)
      (bind pp (Transformation|GetActorLocation :self {PL}))
      (if (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pp) {g('TX')}) (- (.y pp) {g('TY')}) 0.0)) 280.0)
        (bind ch (Utilities|Casting|CastToCharacter :Object {PL})
          (:then (Character|LaunchCharacter :self ch :LaunchVelocity (Math|Vector|MakeVector (* (- (.x pp) {g('TX')}) 1.5) (* (- (.y pp) {g('TY')}) 1.5) 280.0) :bXYOverride true :bZOverride true))
          (:CastFailed))))
    (else
      (if (> {g('T')} {g('Next')})
        (Variables|Default|SetFly true)
        (Variables|Default|SetT 0.0)
        (bind pl (Transformation|GetActorLocation :self {PL}))
        (Variables|Default|SetTX (+ (.x pl) (Math|Random|RandomFloatinRange :Min 450.0 :Max 1600.0)))
        (Variables|Default|SetTY (+ (.y pl) (Math|Random|RandomFloatinRange :Min -900.0 :Max 900.0)))
        (Variables|Default|SetTZ 35.0)
        (bind me (Transformation|GetActorLocation))
        (Variables|Default|SetOX (.x me))
        (Variables|Default|SetOY (.y me))
        (Variables|Default|SetOZ (+ (.z me) 420.0))
        (Audio|PlaySoundatLocation :Sound {g('Launch')} :Location me :VolumeMultiplier 0.9)))))
"""
    r = TG.run(p, code, clear=True)
    editable(p, ["Rock", "Launch", "Impact", "Dust", "Next"], {"Next": 4.0}); return str(r)[:300]

# ---------------- level ----------------
RUN = ["Running", "RunFast", "Run_02"]
HIDE = ["CrouchLookAroundBow", "Cautious_Crouch_Walk_Forward", "Sword_Shout"]
FIGHT = ["Right_Hand_Sword_Slash", "Sword_Judgment", "Shield_Push_Left", "Sword_Parry", "Sword_Parry_Backward_1", "Sword_Parry_Backward_2", "Sword_Parry_Backward_3", "Right_Hand_Sword_Slash", "Sword_Judgment", "Face_Punch_Reaction"]
def soldier(name, x, y, z, yaw, anim, folder, sword=True, pos=None):
    a = E.spawn_actor_from_class(unreal.SkeletalMeshActor, V(x, y, z), unreal.Rotator(roll=0, pitch=0, yaw=yaw + 180))
    c = a.skeletal_mesh_component; c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_skeletal_mesh_asset(EAL.load_asset(random.choice(MESHES)))
    c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    d = unreal.SingleAnimationPlayData(); d.set_editor_property("anim_to_play", A(anim)); d.set_editor_property("saved_looping", True); d.set_editor_property("saved_playing", True)
    d.set_editor_property("saved_position", random.uniform(0, 1) if pos is None else pos); d.set_editor_property("saved_play_rate", random.uniform(0.9, 1.1))
    c.set_editor_property("animation_data", d); c.set_collision_profile_name("NoCollision"); a.set_actor_enable_collision(False)
    s = random.uniform(0.93, 1.07); a.set_actor_scale3d(V(s, s, s))
    c.set_editor_property("visibility_based_anim_tick_option", unreal.VisibilityBasedAnimTickOption.ONLY_TICK_POSE_WHEN_RENDERED)
    a.set_actor_label(name); a.set_folder_path(folder)
    if sword:
        w = E.spawn_actor_from_class(unreal.StaticMeshActor, V(x, y, z)); w.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        w.static_mesh_component.set_static_mesh(EAL.load_asset(SWORD)); w.static_mesh_component.set_collision_profile_name("NoCollision"); w.set_actor_enable_collision(False)
        w.attach_to_component(c, "hand_r", unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.KEEP_WORLD, False)
        w.root_component.set_relative_rotation(unreal.Rotator(roll=180, pitch=0, yaw=90), False, False)
        w.root_component.set_relative_location(V(0, 0, 0.4), False, False)
        w.set_actor_label(name + "_Sword"); w.set_folder_path(folder)
    return a

def level():
    out = {}
    random.seed(1313)
    n = 0
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label()
        if lab.startswith(("Runner_", "DuelPair_", "Duel_", "Hunter_", "Crowd_", "Soldier_", "Rider", "Artillery", "TestSoldier", "Wander_", "Knight_", "Catapult_", "CatRock_", "Duel2_")):
            E.destroy_actor(a); n += 1
    out["removed"] = n
    obs = M.obstacles()
    o, e = M.find("War_Ground").get_actor_bounds(False) if hasattr(M, "find") else (None, None)
    gx0, gx1, gy0, gy1 = -400.0, 6400.0, -4300.0, 4300.0
    def ok(x, y, pad=70): return gx0 < x < gx1 and gy0 < y < gy1 and abs(y) > 950 and not any(M.inside(x, y, b, pad) for b in obs)
    def clear(x0, y0, x1, y1):
        dx, dy = x1 - x0, y1 - y0; L_ = math.hypot(dx, dy)
        return L_ > 1 and M.first_hit(x0, y0, dx / L_, dy / L_, L_, obs, 35) is None and (y0 > 0) == (y1 > 0)
    def near_cover():
        b = random.choice(obs); side = random.choice([0, 1, 2, 3])
        x = random.uniform(b[1], b[2]); y = random.uniform(b[3], b[4])
        if side == 0: x = b[1] - 110
        if side == 1: x = b[2] + 110
        if side == 2: y = b[3] - 110
        if side == 3: y = b[4] + 110
        return x, y
    # wanderers: three points (one next to cover), segments clear
    wcls = EAL.load_asset(f"{WB}/BP_Wanderer").generated_class(); made = 0; tries = 0
    while made < 28 and tries < 40000:
        tries += 1
        p0 = near_cover(); sg = 1 if p0[1] > 0 else -1
        pts = [p0] + [(p0[0] + random.uniform(-1500, 1500), sg * random.uniform(1000, 4200)) for _ in range(2)]
        if not all(ok(*p) for p in pts): continue
        if not (clear(*pts[0], *pts[1]) and clear(*pts[1], *pts[2]) and clear(*pts[2], *pts[0])): continue
        if min(math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]) for i, j in ((0, 1), (1, 2), (2, 0))) < 350: continue
        x, y = pts[0]
        w = E.spawn_actor_from_class(wcls, V(x, y, 0), unreal.Rotator()); w.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        body = soldier(f"Wander_{made}_Body", x, y, 2, 0, random.choice(RUN), "Art/War/Battle/Wanderers", sword=random.random() < 0.6)
        body.attach_to_actor(w, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        for k, (px, py) in zip("ABC", pts): w.set_editor_property(f"{k}X", float(px)); w.set_editor_property(f"{k}Y", float(py))
        w.set_editor_property("Speed", random.uniform(300, 470)); w.set_editor_property("Body", body)
        w.set_editor_property("RunAnim", A(random.choice(RUN))); w.set_editor_property("HideAnim", A(random.choice(HIDE)))
        w.set_actor_label(f"Wander_{made}"); w.set_folder_path("Art/War/Battle/Wanderers"); made += 1
    out["wanderers"] = made
    # duels (sword fights in place)
    dcls = EAL.load_asset(f"{WB}/BP_DuelPair").generated_class(); made = 0; tries = 0
    while made < 12 and tries < 3000:
        tries += 1
        x = random.uniform(gx0, gx1); y = random.choice([-1, 1]) * random.uniform(1050, 3800); yaw = random.uniform(0, 360)
        dx, dy = math.cos(math.radians(yaw)) * 75, math.sin(math.radians(yaw)) * 75
        if not (ok(x - dx, y - dy, 110) and ok(x + dx, y + dy, 110)): continue
        a_ = soldier(f"Duel2_{made}a", x - dx, y - dy, 2, yaw, random.choice(FIGHT), "Art/War/Battle/Duels")
        b_ = soldier(f"Duel2_{made}b", x + dx, y + dy, 2, yaw + 180, random.choice(FIGHT), "Art/War/Battle/Duels")
        c = E.spawn_actor_from_class(dcls, V(x, y, 100), unreal.Rotator())
        c.set_editor_property("A", a_); c.set_editor_property("B", b_)
        for i, nm in enumerate(FIGHT): c.set_editor_property(f"Anim{i}", A(nm))
        try:
            c.set_editor_property("Clang", EAL.load_asset(f"{R}/Audio/SFX/SFX_SwordClang"))
        except Exception: pass
        c.set_actor_label(f"Duel2_{made}"); c.set_folder_path("Art/War/Battle/Duels"); made += 1
    out["duels"] = made
    # knights in the lane, ahead of the player
    kcls = EAL.load_asset(f"{WB}/BP_Knight").generated_class(); made = 0; tries = 0
    shout = None
    for pth in (f"{R}/Audio/SFX/SFX_BattleShout", f"{R}/Audio/SFX/SFX_SwordClang"):
        if EAL.does_asset_exist(pth): shout = EAL.load_asset(pth); break
    kxs = []
    while made < 6 and tries < 3000:
        tries += 1
        x = random.uniform(900, 5400); y = random.uniform(-520, 520)
        if any(M.inside(x, y, b, 50) for b in obs) or any(abs(x - kx) < 450 for kx in kxs): continue
        kxs.append(x)
        k = E.spawn_actor_from_class(kcls, V(x, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=180)); k.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        body = soldier(f"Knight_{made}_Body", x, y, 2, 180, "Sword_Parry", "Art/War/Battle/Knights", pos=0.0)
        body.attach_to_actor(k, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        for kk, vv in (("Body", body), ("RunAnim", A("RunFast")), ("IdleAnim", A("Sword_Parry")), ("HitAnim", A("Right_Hand_Sword_Slash")), ("DieAnim", A("dying_backwards"))): k.set_editor_property(kk, vv)
        clang = EAL.load_asset(f"{R}/Audio/SFX/SFX_SwordClang"); k.set_editor_property("Clang", clang); k.set_editor_property("Shout", shout or clang)
        k.set_actor_label(f"Knight_{made}"); k.set_folder_path("Art/War/Battle/Knights"); made += 1
    out["knights"] = made
    # catapults on the flanks, each with its own stone
    ccls = EAL.load_asset(f"{WB}/BP_Catapult").generated_class(); cm = EAL.load_asset(f"{WB}/Catapult/catapult")
    bb = cm.get_bounding_box(); length = max(bb.max.x - bb.min.x, bb.max.y - bb.min.y); sc = 520.0 / max(length, 1)
    spots = [(1600, 2700, -100), (3600, -2900, 100), (5400, 2500, -110)]
    rk = EAL.load_asset(ROCK); rb = rk.get_bounding_box(); rs = 70.0 / max(rb.max.z - rb.min.z, 1)
    out["cat"] = []
    for i, (x, y, yaw) in enumerate(spots):
        # nudge out of obstacles
        for _ in range(40):
            if not any(M.inside(x, y, b, 300) for b in obs): break
            x += random.uniform(-300, 300); y += random.uniform(-200, 200) * (1 if y > 0 else -1)
        z = M.ground_z(x, y) or 0.0
        cat = E.spawn_actor_from_class(unreal.StaticMeshActor, V(x, y, z - bb.min.z * sc), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
        cat.static_mesh_component.set_static_mesh(cm); cat.set_actor_scale3d(V(sc, sc, sc)); cat.set_actor_label(f"Catapult_{i}"); cat.set_folder_path("Art/War/Battle/Catapults")
        cat.static_mesh_component.set_collision_profile_name("BlockAll")
        rock = E.spawn_actor_from_class(unreal.StaticMeshActor, V(x, y, z + 300)); rock.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        rock.static_mesh_component.set_static_mesh(rk); rock.set_actor_scale3d(V(rs, rs, rs)); rock.static_mesh_component.set_collision_profile_name("NoCollision"); rock.set_actor_enable_collision(False)
        rock.set_actor_label(f"CatRock_{i}"); rock.set_folder_path("Art/War/Battle/Catapults")
        ctl = E.spawn_actor_from_class(ccls, V(x, y, z), unreal.Rotator()); ctl.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        ctl.set_editor_property("Rock", rock); ctl.set_editor_property("Launch", EAL.load_asset(f"{R}/Audio/SFX/SFX_CatapultLaunch"))
        ctl.set_editor_property("Impact", EAL.load_asset(f"{R}/Audio/SFX/SFX_StoneImpact"))
        try: ctl.set_editor_property("Dust", EAL.load_asset("/Game/Effects/NS_SmokeBillow") if EAL.does_asset_exist("/Game/Effects/NS_SmokeBillow") else None)
        except Exception: pass
        ctl.set_editor_property("Next", 2.0 + i * 1.7); ctl.set_actor_label(f"Catapult_{i}_Ctl"); ctl.set_folder_path("Art/War/Battle/Catapults")
        out["cat"].append([round(x), round(y), round(z)])
    # HUD line
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "HUD_0":
            a.text_render.set_text(unreal.Text("Reach the checkpoint. Dodge the catapult stones. Hide behind rocks from the knights, or SHIFT (Cut Boost) into one to knock him down."))
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("wanderer", wanderer)
    if not res["err"]: step("level", level)
    return res
