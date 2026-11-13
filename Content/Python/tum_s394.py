# War v3: open battlefield (no corridor, no rows), roam anywhere to the checkpoint; knights patrol and only chase with line of sight,
# no sound spam (cooldowns), boulders as cover everywhere, solid walkable planks
import unreal, importlib, traceback, math, random
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
import tum_s364b as S; importlib.reload(S)
EAL = unreal.EditorAssetLibrary; E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"; MS = "/Game/MS/3D"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
def play(var, anim, loop="true"): return f"(Components|Animation|PlayAnimation :self (Class|SkeletalMeshActor|GetSkeletalMeshComponent :self {g(var)}) :NewAnimToPlay {anim} :bLooping {loop})"
def sms(folder):
    try: return [EAL.load_asset(p) for p in EAL.list_assets(folder, False, False) if p.split("/")[-1].startswith("SM_")]
    except Exception: return []

def knight():
    p = f"{WB}/BP_Knight"
    TG.ensure_vars(p, [("State", "int"), ("HomeX", "float"), ("HomeY", "float"), ("PX", "float"), ("PY", "float"), ("Chase", "float"),
                       ("Speed", "float"), ("Sight", "float"), ("Cool", "float"), ("ShoutT", "float")],
                   objs=[("Body", unreal.SkeletalMeshActor.static_class()), ("RunAnim", unreal.AnimSequence.static_class()), ("IdleAnim", unreal.AnimSequence.static_class()),
                         ("WalkAnim", unreal.AnimSequence.static_class()), ("HitAnim", unreal.AnimSequence.static_class()), ("DieAnim", unreal.AnimSequence.static_class()),
                         ("Shout", unreal.SoundBase.static_class()), ("Clang", unreal.SoundBase.static_class())])
    trace = lambda frm, to: f"(Collision|LineTraceByChannel :Start {frm} :End {to})"
    ahead = lambda dist: f"(Math|Vector|MakeVector (+ (.x me) (* (.x dir) {dist})) (+ (.y me) (* (.y dir) {dist})) (+ (.z me) 90.0))"
    newpt = f"""(Variables|Default|SetPX (+ {g('HomeX')} (Math|Random|RandomFloatinRange :Min -1300.0 :Max 1300.0)))
        (Variables|Default|SetPY (+ {g('HomeY')} (Math|Random|RandomFloatinRange :Min -1300.0 :Max 1300.0)))"""
    code = f"""
(event EventBeginPlay
  (bind l (Transformation|GetActorLocation))
  (Variables|Default|SetHomeX (.x l))
  (Variables|Default|SetHomeY (.y l))
  (Variables|Default|SetPX (.x l))
  (Variables|Default|SetPY (.y l))
  (Variables|Default|SetCool 1.0)
  (Variables|Default|SetState 0))

(event EventTick (DeltaSeconds)
  (bind me (Transformation|GetActorLocation))
  (bind pp (Transformation|GetActorLocation :self {PL}))
  (bind d (Transformation|GetDistanceTo :OtherActor {PL}))
  (Variables|Default|SetShoutT (- {g('ShoutT')} DeltaSeconds))
  (bind los (not {trace('(Math|Vector|MakeVector (.x me) (.y me) (+ (.z me) 120.0))', '(Math|Vector|MakeVector (- (.x pp) (* (/ (- (.x pp) (.x me)) (+ d 1.0)) 70.0)) (- (.y pp) (* (/ (- (.y pp) (.y me)) (+ d 1.0)) 70.0)) (+ (.z pp) 40.0))')}))
  (if (== {g('State')} 4)
    (Variables|Default|SetCool (- {g('Cool')} DeltaSeconds))
    (if (< {g('Cool')} 0.0)
      (Variables|Default|SetState 0)
      {newpt}
      {play('Body', g('WalkAnim'))}))
  (if (== {g('State')} 0)
    (bind tgt (Math|Vector|MakeVector {g('PX')} {g('PY')} (.z me)))
    (bind dir (Math|Vector|GetForwardVector :InRot (Math|Rotator|FindLookatRotation :Start me :Target tgt)))
    (if (or (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x me) {g('PX')}) (- (.y me) {g('PY')}) 0.0)) 60.0) {trace(ahead(40.0), ahead(160.0))})
      {newpt}
      (else
        (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterptoConstant :Current me :Target tgt :DeltaTime DeltaSeconds :InterpSpeed 150.0) :bTeleport true)
        (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start me :Target tgt) :bTeleportPhysics true)))
    (if (and los (< d {g('Sight')}))
      (Variables|Default|SetState 1)
      (Variables|Default|SetChase 0.0)
      {play('Body', g('RunAnim'))}
      (if (< {g('ShoutT')} 0.0)
        (Variables|Default|SetShoutT 6.0)
        (Audio|PlaySoundatLocation :Sound {g('Shout')} :Location me :VolumeMultiplier 0.8))))
  (if (== {g('State')} 1)
    (Variables|Default|SetChase (+ {g('Chase')} DeltaSeconds))
    (bind tgt2 (Math|Vector|MakeVector (.x pp) (.y pp) (.z me)))
    (bind dir (Math|Vector|GetForwardVector :InRot (Math|Rotator|FindLookatRotation :Start me :Target tgt2)))
    (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start me :Target tgt2) :bTeleportPhysics true)
    (if (and (> d 190.0) (not {trace(ahead(40.0), ahead(150.0))}))
      (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterptoConstant :Current me :Target tgt2 :DeltaTime DeltaSeconds :InterpSpeed {g('Speed')}) :bTeleport true))
    (if (< d 190.0)
      (if (> (Math|Vector|VectorLength (Math|Vector|MakeVector (.x (Transformation|GetVelocity :self {PL})) (.y (Transformation|GetVelocity :self {PL})) 0.0)) 700.0)
        (Variables|Default|SetState 3)
        {play('Body', g('DieAnim'), 'false')}
        (Audio|PlaySoundatLocation :Sound {g('Clang')} :Location me :VolumeMultiplier 1.0 :PitchMultiplier 0.85)
        (else
          (Variables|Default|SetState 4)
          (Variables|Default|SetCool 2.5)
          {play('Body', g('HitAnim'), 'false')}
          (Audio|PlaySoundatLocation :Sound {g('Clang')} :Location me :VolumeMultiplier 0.9)
          (bind ch (Utilities|Casting|CastToCharacter :Object {PL})
            (:then (Character|LaunchCharacter :self ch :LaunchVelocity (Math|Vector|MakeVector (* (- (.x pp) (.x me)) 3.0) (* (- (.y pp) (.y me)) 3.0) 250.0) :bXYOverride true :bZOverride true))
            (:CastFailed))))
      (else
        (if (or (or (not los) (> d (* {g('Sight')} 1.6))) (> {g('Chase')} 9.0))
          (Variables|Default|SetState 4)
          (Variables|Default|SetCool 1.5)
          {play('Body', g('IdleAnim'))})))))
"""
    r = TG.run(p, code, clear=True)
    S.editable(p, ["Body", "RunAnim", "IdleAnim", "WalkAnim", "HitAnim", "DieAnim", "Shout", "Clang", "Speed", "Sight"], {"Speed": 330.0, "Sight": 1100.0}); return str(r)[:300]

def level():
    out = {}
    random.seed(4242)
    gone = []
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label()
        if lab.startswith(("Art_Old_Wood_Boards", "Trench_", "Art_Stakes_And_Wedge", "LaneWall", "Cover_Wall", "Knight_", "Bound_War", "Cover_Boulder")):
            gone.append(lab); E.destroy_actor(a)
    out["removed"] = len(gone)
    # field limits the player cannot leave (invisible), far enough to feel open
    inv = EAL.load_asset(f"{R}/Materials/Surfaces/M_Invisible"); cube = EAL.load_asset("/Engine/BasicShapes/Cube")
    for i, (x, y, sx, sy) in enumerate([(-900, 0, 0.5, 100), (7300, 0, 0.5, 100), (3200, -4700, 90, 0.5), (3200, 4700, 90, 0.5)]):
        b = E.spawn_actor_from_class(unreal.StaticMeshActor, V(x, y, 400)); b.static_mesh_component.set_static_mesh(cube)
        b.set_actor_scale3d(V(sx, sy, 10)); b.static_mesh_component.set_material(0, inv); b.static_mesh_component.set_collision_profile_name("BlockAll")
        b.static_mesh_component.set_cast_shadow(False); b.set_actor_label(f"Bound_War_{i}"); b.set_folder_path("Art/War/Bounds")
    # cover: boulders scattered (never in a row), off soldier paths
    segs = []
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("Wander_") and not lab.endswith(("Body", "Sword")):
            p = [(a.get_editor_property(f"{k}X"), a.get_editor_property(f"{k}Y")) for k in "ABC"]; segs += [(p[0], p[1]), (p[1], p[2]), (p[2], p[0])]
        if lab.startswith("Duel2_") and not lab.endswith(("a", "b", "Sword")):
            l = a.get_actor_location(); segs.append(((l.x - 150, l.y), (l.x + 150, l.y)))
    def segd(px, py, a, b):
        ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); return math.hypot(px - ax - t * dx, py - ay - t * dy)
    boulders = sms(f"{MS}/Beach_Boulder_uisjbbis") + sms(f"{MS}/Beach_Boulder_ukopdins") + sms(f"{MS}/Beach_Boulder_ukopeess") + sms(f"{MS}/Nordic_Beach_Boulder_vcyqebjfa") + sms(f"{MS}/Limestone_Slab_ubxbadpda")
    obs = M.obstacles(); n = 0; tries = 0
    while n < 34 and tries < 6000:
        tries += 1
        x = random.uniform(300, 6400); y = random.uniform(-4100, 4100); size = random.uniform(170, 300)
        if math.hypot(x, y) < 500 or math.hypot(x - 5650, y + 330) < 500: continue
        if any(M.inside(x, y, b, size * 0.7 + 80) for b in obs): continue
        if any(segd(x, y, *s) < size * 0.6 + 110 for s in segs): continue
        m = random.choice(boulders)
        a = E.spawn_actor_from_object(m, V(0, 0, 0), unreal.Rotator(roll=random.uniform(-6, 6), pitch=random.uniform(-6, 6), yaw=random.uniform(0, 360)))
        o, e = a.get_actor_bounds(False); s = size / max(2 * max(e.x, e.y), 1)
        a.set_actor_scale3d(V(s, s, s * random.uniform(0.7, 1.1)))
        o, e = a.get_actor_bounds(False); l = a.get_actor_location()
        a.set_actor_location(V(l.x + x - o.x, l.y + y - o.y, l.z - (o.z - e.z) - 25), False, False)
        a.static_mesh_component.set_collision_profile_name("BlockAll"); a.set_actor_label(f"Cover_Boulder_{n}"); a.set_folder_path("Art/War/Cover")
        obs.append((a, o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y)); n += 1
    out["boulders"] = n
    # knights: patrol anywhere in the field
    kcls = EAL.load_asset(f"{WB}/BP_Knight").generated_class(); made = 0; tries = 0; ks = []
    clashes = [EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Clash_{i}") for i in range(1, 11)]
    swing = EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Swing_2")
    while made < 8 and tries < 4000:
        tries += 1
        x = random.uniform(900, 6000); y = random.uniform(-3600, 3600)
        if any(M.inside(x, y, b, 150) for b in obs) or any(math.hypot(x - kx, y - ky) < 1300 for kx, ky in ks): continue
        ks.append((x, y))
        k = E.spawn_actor_from_class(kcls, V(x, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360))); k.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        body = S.soldier(f"Knight_{made}_Body", x, y, 2, 180, "Walking", "Art/War/Battle/Knights")
        body.attach_to_actor(k, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        body.set_actor_relative_rotation(unreal.Rotator(0, 0, 180), False, False) if hasattr(body, "set_actor_relative_rotation") else None
        for kk, vv in (("Body", body), ("RunAnim", S.A("RunFast")), ("IdleAnim", S.A("Sword_Parry")), ("WalkAnim", S.A("Walking")), ("HitAnim", S.A("Right_Hand_Sword_Slash")), ("DieAnim", S.A("dying_backwards"))):
            k.set_editor_property(kk, vv)
        k.set_editor_property("Clang", random.choice(clashes)); k.set_editor_property("Shout", swing)
        k.set_actor_label(f"Knight_{made}"); k.set_folder_path("Art/War/Battle/Knights"); made += 1
    out["knights"] = made
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "HUD_0":
            a.text_render.set_text(unreal.Text("Cross the battlefield any way you like to the lantern checkpoint. Knights chase you if they see you: hide behind rocks, or SHIFT (Cut Boost) into one to knock him down."))
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("knight", knight)
    if not res["err"]: step("level", level)
    return res
