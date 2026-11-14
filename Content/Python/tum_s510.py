# War, chaotic: animated catapults far away that chase you with stones, archer volleys, more knights/duels, a bigger field.
import unreal, importlib, traceback, random, math
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
import tum_s364b as S; importlib.reload(S)
import tum_s500 as P; importlib.reload(P)
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"; MS = "/Game/MS/3D"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
NP = 10; NA = 6
X1 = 10100.0
PIVOT = (-65.0, -0.8, 37.0); REST = -13.37; UP = 98.0; CUP = (157.0, 0.0, 12.0)
def hurt(dmg):
    return (f"(bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object {PL})\n"
            f"          (:then (Class|BPTUMCharacter|SetHealth :self ch :Health (- (Class|BPTUMCharacter|GetHealth :self ch) {dmg}))\n"
            f"                 (Class|BPTUMCharacter|SetLastHit :self ch :LastHit (Utilities|Time|GetGameTimeinSeconds)))\n"
            f"          (:CastFailed))")

# ---------------------------------------------------------------- catapult with a swinging arm, far away, leading the player
def catapult_bp():
    p = f"{WB}/BP_Catapult"
    TG.ensure_vars(p, [(n, "float") for n in ("T", "Next", "OX", "OY", "OZ", "TX", "TY", "TZ", "RockZ", "FlightT", "Arc")] + [("Phase", "int"), ("Idx", "int"), ("bLoaded", "bool"), ("bOpener", "bool"), ("Shots", "int")],
                   objs=[("Crater", unreal.Actor.static_class()), ("Rock", unreal.StaticMeshActor.static_class()), ("Launch", unreal.SoundBase.static_class()), ("Impact", unreal.SoundBase.static_class()),
                         ("Dust", unreal.NiagaraSystem.static_class()), ("Trail", unreal.NiagaraSystem.static_class()), ("Cat", unreal.StaticMeshActor.static_class()), ("Arm", unreal.StaticMeshActor.static_class())]
                        + [(f"Pool{k}", unreal.StaticMeshActor.static_class()) for k in range(NP)])
    pick = "\n".join(f"        (if (== {g('Idx')} {k}) (Variables|Default|SetRock {g(f'Pool{k}')}))" for k in range(NP))
    arm = lambda pitch: f"(Transformation|SetActorRelativeRotation :self {g('Arm')} :NewRelativeRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch {pitch} :Yaw 0.0))"
    code = f"""
(event EventTick (DeltaSeconds)
  (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
  (bind me (Transformation|GetActorLocation))
  (bind cup (Math|Transform|TransformLocation :T (Transformation|GetActorTransform :self {g('Arm')}) :Location (Math|Vector|MakeVector {CUP[0]} {CUP[1]} {CUP[2]})))
  (bind pl (Transformation|GetActorLocation :self {PL}))
  (if (== {g('Phase')} 0)
    {arm(str(REST))}
    (bind yaw (+ (Math|Trig|Atan2(Degrees) (- (.y pl) (.y me)) (- (.x pl) (.x me))) 180.0))
    (Transformation|SetActorRotation :NewRotation (Math|Interpolation|RInterpTo :Current (Transformation|GetActorRotation) :Target (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw yaw) :DeltaTime DeltaSeconds :InterpSpeed 1.5) :bTeleportPhysics true)
    (if (and (> {g('T')} 0.8) (not {g('Loaded')}))
      (Variables|Default|SetLoaded true)
      (Variables|Default|SetIdx (+ {g('Idx')} 1))
      (if (> {g('Idx')} {NP - 1}) (Variables|Default|SetIdx 0))
{pick})
    (if {g('Loaded')}
      (Transformation|SetActorLocation :self {g('Rock')} :NewLocation cup :bTeleport true))
    (if (and (and {g('Loaded')} (> {g('T')} {g('Next')})) (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pl) (.x me)) (- (.y pl) (.y me)) 0.0)) 7500.0))
      (Variables|Default|SetPhase 1)
      (Variables|Default|SetT 0.0)))
  (if (== {g('Phase')} 1)
    (bind s (Math|Float|Min(Float) (/ {g('T')} 0.34) 1.0))
    {arm(f"(+ {REST} (* (- {UP} {REST}) (* s s)))")}
    (Transformation|SetActorLocation :self {g('Rock')} :NewLocation cup :bTeleport true)
    (if (> s 0.99)
      (Variables|Default|SetPhase 2)
      (Variables|Default|SetT 0.0)
      (bind pv (Transformation|GetVelocity :self {PL}))
      (bind dist (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pl) (.x cup)) (- (.y pl) (.y cup)) 0.0)))
      (Variables|Default|SetFlightT (Math|Float|Clamp(Float) (/ dist 1700.0) 1.6 3.2))
      (Variables|Default|SetArc (+ 500.0 (* dist 0.32)))
      (if (and {g('Opener')} (== {g('Shots')} 0))
        (Variables|Default|SetTX (+ (.x pl) 420.0))
        (Variables|Default|SetTY (+ (.y pl) 160.0))
        (else
          (Variables|Default|SetTX (+ (+ (.x pl) (* (.x pv) (* {g('FlightT')} 0.85))) (Math|Random|RandomFloatinRange :Min -220.0 :Max 220.0)))
          (Variables|Default|SetTY (+ (+ (.y pl) (* (.y pv) (* {g('FlightT')} 0.85))) (Math|Random|RandomFloatinRange :Min -220.0 :Max 220.0)))))
      (Variables|Default|SetTZ {g('RockZ')})
      (Variables|Default|SetOX (.x cup))
      (Variables|Default|SetOY (.y cup))
      (Variables|Default|SetOZ (.z cup))
      (Niagara|SpawnSystemAttached :SystemTemplate {g('Trail')} :AttachToComponent (Class|StaticMeshActor|GetStaticMeshComponent :self {g('Rock')}) :bAutoDestroy true)
      (Audio|PlaySoundatLocation :Sound {g('Launch')} :Location me :VolumeMultiplier 1.6)))
  (if (== {g('Phase')} 2)
    (bind a (/ {g('T')} {g('FlightT')}))
    (bind h (* (Math|Trig|Sin(Radians) (* (Math|Float|Min(Float) a 1.0) 3.14159)) {g('Arc')}))
    (bind am (Math|Float|Min(Float) a 1.0))
    (Transformation|SetActorLocation :self {g('Rock')} :NewLocation (Math|Vector|MakeVector (+ {g('OX')} (* (- {g('TX')} {g('OX')}) am)) (+ {g('OY')} (* (- {g('TY')} {g('OY')}) am)) (+ (+ {g('OZ')} (* (- {g('TZ')} {g('OZ')}) am)) h)) :bTeleport true)
    (Transformation|AddActorLocalRotation :self {g('Rock')} :DeltaRotation (Math|Rotator|MakeRotator :Roll (* DeltaSeconds 200.0) :Pitch (* DeltaSeconds 300.0) :Yaw 0.0))
    {arm(f"(+ {UP} (* ({REST} - {UP}) 0.0))") if False else arm(f"(+ {UP} (* (- {REST} {UP}) (Math|Float|Min(Float) (/ {g('T')} 1.6) 1.0)))")}
    (if (> a 1.0)
      (Variables|Default|SetPhase 0)
      (Variables|Default|SetT 0.0)
      (Variables|Default|SetLoaded false)
      (Variables|Default|SetNext (Math|Random|RandomFloatinRange :Min 4.0 :Max 7.0))
      (bind tg (Math|Vector|MakeVector {g('TX')} {g('TY')} {g('TZ')}))
      (Transformation|SetActorLocation :self {g('Rock')} :NewLocation tg :bTeleport true)
      (Audio|PlaySoundatLocation :Sound {g('Impact')} :Location tg :VolumeMultiplier 1.4 :PitchMultiplier (Math|Random|RandomFloatinRange :Min 0.85 :Max 1.1))
      (Niagara|SpawnSystematLocation :SystemTemplate {g('Dust')} :Location tg :Scale (Math|Vector|MakeVector 1.6 1.6 1.6))
      (Transformation|SetActorLocation :self {g('Crater')} :NewLocation (Math|Vector|MakeVector {g('TX')} {g('TY')} 0.0) :bTeleport true)
      (Variables|Default|SetShots (+ {g('Shots')} 1))
      (bind dd (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pl) {g('TX')}) (- (.y pl) {g('TY')}) 0.0)))
      (if (< dd 300.0)
        (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object {PL})
          (:then
              (Character|LaunchCharacter :self ch :LaunchVelocity (Math|Vector|MakeVector (* (- (.x pl) {g('TX')}) 1.5) (* (- (.y pl) {g('TY')}) 1.5) 300.0) :bXYOverride true :bZOverride true)
              (Class|BPTUMCharacter|SetHealth :self ch :Health (- (Class|BPTUMCharacter|GetHealth :self ch) (+ 25.0 (* 40.0 (- 1.0 (/ dd 300.0))))))
              (Class|BPTUMCharacter|SetLastHit :self ch :LastHit (Utilities|Time|GetGameTimeinSeconds)))
          (:CastFailed))))))
"""
    r = TG.run(p, code, clear=True)
    S.editable(p, ["Rock", "Launch", "Impact", "Dust", "Trail", "Cat", "Arm", "Next", "Crater", "bOpener", "RockZ", "bLoaded"] + [f"Pool{k}" for k in range(NP)], {"Next": 4.0, "bLoaded": False, "RockZ": 0.0})
    return str(r)[:200]

def catapults_level():
    random.seed(99)
    base_m = EAL.load_asset(f"{WB}/Catapult/SM_CatapultBase"); arm_m = EAL.load_asset(f"{WB}/Catapult/SM_CatapultArm")
    old = [a for a in E.get_all_level_actors() if a.get_actor_label().startswith("Catapult_") and a.get_actor_label().endswith("_Ctl")]
    tmpl = old[0]
    keep = {k: tmpl.get_editor_property(k) for k in ("Launch", "Impact", "Dust", "Trail")}
    keep["Launch"] = keep["Launch"] or EAL.load_asset(f"{R}/Audio/SFX/SFX_CatapultLaunch"); keep["Impact"] = keep["Impact"] or EAL.load_asset(f"{R}/Audio/SFX/SFX_StoneImpact")
    crater = {a.get_actor_label(): a for a in E.get_all_level_actors() if a.get_actor_label().startswith("Crater_") and "_Rubble" not in a.get_actor_label()}
    rock_mesh = EAL.load_asset(S.ROCK); rb = rock_mesh.get_bounding_box(); rs = 70.0 / max(rb.max.z - rb.min.z, 1); rock_sc = V(rs, rs, rs)
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label()
        if lab.startswith(("Catapult_", "CatRock_")): E.destroy_actor(a)
    ccls = EAL.load_asset(f"{WB}/BP_Catapult").generated_class()
    spots = [(1800, -5600), (4300, 5700), (6200, -5800), (8200, 5600), (9600, -5400), (2600, 5800)]
    sc = 2.6; out = []
    for i, (x, y) in enumerate(spots):
        z = M.ground_z(x, y) or 0.0
        ctl = E.spawn_actor_from_class(ccls, V(x, y, z), unreal.Rotator(roll=0, pitch=0, yaw=math.degrees(math.atan2(-y, 4000 - x)) + 180))
        ctl.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        bb = base_m.get_bounding_box()
        cat = E.spawn_actor_from_object(base_m, V(x, y, z - bb.min.z * sc)); cat.set_actor_scale3d(V(sc, sc, sc))
        cat.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE); cat.static_mesh_component.set_collision_profile_name("BlockAll")
        cat.attach_to_actor(ctl, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        cat.set_actor_relative_rotation(unreal.Rotator(roll=0, pitch=0, yaw=0), False, False)
        arm = E.spawn_actor_from_object(arm_m, V(x, y, z)); arm.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        arm.static_mesh_component.set_collision_profile_name("NoCollision")
        arm.attach_to_actor(cat, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        arm.root_component.set_relative_scale3d(V(1, 1, 1)); arm.root_component.set_relative_location(V(*PIVOT), False, False)
        arm.set_actor_relative_rotation(unreal.Rotator(roll=0, pitch=REST, yaw=0), False, False)
        cat.set_actor_label(f"Catapult_{i}"); arm.set_actor_label(f"Catapult_{i}_Arm"); ctl.set_actor_label(f"Catapult_{i}_Ctl")
        for a_ in (cat, arm, ctl): a_.set_folder_path("Art/War/Battle/Catapults")
        for k, v in keep.items(): ctl.set_editor_property(k, v)
        ctl.set_editor_property("Cat", cat); ctl.set_editor_property("Arm", arm)
        cr = crater.get(f"Crater_{i % 3}")
        if cr: ctl.set_editor_property("Crater", cr)
        pools = []
        for k in range(NP):
            s = E.spawn_actor_from_object(rock_mesh, V(x, y, -20000 - k * 300 - i * 4000)); s.set_actor_scale3d(rock_sc)
            s.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE); s.static_mesh_component.set_collision_profile_name("BlockAll")
            s.set_actor_label(f"CatRock_{i}_P{k}"); s.set_folder_path("Art/War/Battle/Catapults"); pools.append(s); ctl.set_editor_property(f"Pool{k}", s)
        ctl.set_editor_property("RockZ", -8.0); ctl.set_editor_property("bOpener", i == 0); ctl.set_editor_property("Next", 1.2 if i == 0 else 2.5 + i * 0.9)
        ctl.set_editor_property("Rock", pools[0])
        out.append([round(x), round(y)])
    return out

# ---------------------------------------------------------------- arrows
def arrow_mesh():
    p = f"{WB}/Archers/SM_Arrow"
    if EAL.does_asset_exist(p): return "exists"
    dm = unreal.DynamicMesh(); O = unreal.GeometryScriptPrimitiveOptions()
    PF = unreal.GeometryScript_Primitives
    ident = unreal.Transform()
    PF.append_cylinder(dm, O, unreal.Transform(location=V(0, 0, 0), rotation=unreal.Rotator(roll=0, pitch=-90, yaw=0)), 0.7, 90.0, 6, 1, True, unreal.GeometryScriptPrimitiveOriginMode.BASE)
    PF.append_cone(dm, O, unreal.Transform(location=V(90, 0, 0), rotation=unreal.Rotator(roll=0, pitch=-90, yaw=0)), 1.8, 0.0, 6.0, 6, 1, True, unreal.GeometryScriptPrimitiveOriginMode.BASE)
    for ang in (0, 120, 240):
        PF.append_box(dm, O, unreal.Transform(location=V(4, 0, 0), rotation=unreal.Rotator(roll=ang, pitch=0, yaw=0)), 10.0, 0.3, 4.0, 0, 0, 0, unreal.GeometryScriptPrimitiveOriginMode.BASE)
    opts = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    try: opts.set_editor_property("enable_collision", False)
    except Exception: pass
    r = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm, p, opts)
    sm = [x for x in (r if isinstance(r, tuple) else (r,)) if isinstance(x, unreal.StaticMesh)][0]
    mat = EAL.load_asset(M.POLE).get_material(0)
    sm.set_material(0, mat); EAL.save_loaded_asset(sm, False)
    return p

def archers_bp():
    p = f"{WB}/BP_Archers"
    if not EAL.does_asset_exist(p):
        from editor_toolset.toolsets.blueprint import BlueprintTools as BT
        BT.create(f"{WB}", "BP_Archers", unreal.Actor.static_class())
    fl = [("T", "float"), ("Next", "float"), ("Dur", "float"), ("Arc", "float"), ("bFly", "bool")]
    for k in range(NA): fl += [(f"S{c}{k}", "float") for c in "XYZ"] + [(f"T{c}{k}", "float") for c in "XYZ"]
    TG.ensure_vars(p, fl, objs=[(f"A{k}", unreal.StaticMeshActor.static_class()) for k in range(NA)] + [("Whoosh", unreal.SoundBase.static_class()), ("Thud", unreal.SoundBase.static_class())])
    pos = lambda k, a: f"(Math|Vector|MakeVector (+ {g(f'SX{k}')} (* (- {g(f'TX{k}')} {g(f'SX{k}')}) {a})) (+ {g(f'SY{k}')} (* (- {g(f'TY{k}')} {g(f'SY{k}')}) {a})) (+ (+ {g(f'SZ{k}')} (* (- {g(f'TZ{k}')} {g(f'SZ{k}')}) {a})) (* {g('Arc')} (* 4.0 (* {a} (- 1.0 {a}))))))"
    fly = "\n".join(f"""    (bind p{k} {pos(k, 'am')})
    (bind q{k} {pos(k, '(+ am 0.02)')})
    (Transformation|SetActorLocationAndRotation :self {g(f'A{k}')} :NewLocation p{k} :NewRotation (Math|Rotator|FindLookatRotation :Start p{k} :Target q{k}) :bTeleport true)""" for k in range(NA))
    nh = " ".join(f"(select (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pl) {g(f'TX{k}')}) (- (.y pl) {g(f'TY{k}')}) 0.0)) 105.0) 12.0 0.0)" for k in range(NA))
    land = f"""      (bind nh (+ {nh.replace(' (select', ' (+ (select', NA - 2)} {')' * (NA - 2)}))
      (if (> nh 0.5)
        {hurt('nh')})"""
    fire = "\n".join(f"""        (Variables|Default|SetSX{k} (+ (.x me) (Math|Random|RandomFloatinRange :Min -250.0 :Max 250.0)))
        (Variables|Default|SetSY{k} (+ (.y me) (Math|Random|RandomFloatinRange :Min -250.0 :Max 250.0)))
        (Variables|Default|SetSZ{k} (+ (.z me) 160.0))
        (Variables|Default|SetTX{k} (+ (+ (.x pl) (* (.x pv) (* {g('Dur')} 0.75))) (Math|Random|RandomFloatinRange :Min -360.0 :Max 360.0)))
        (Variables|Default|SetTY{k} (+ (+ (.y pl) (* (.y pv) (* {g('Dur')} 0.75))) (Math|Random|RandomFloatinRange :Min -360.0 :Max 360.0)))
        (Variables|Default|SetTZ{k} (- (.z pl) 75.0))""" for k in range(NA))
    code = f"""
(event EventTick (DeltaSeconds)
  (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
  (bind me (Transformation|GetActorLocation))
  (bind pl (Transformation|GetActorLocation :self {PL}))
  (if {g('Fly')}
    (bind a (/ {g('T')} {g('Dur')}))
    (bind am (Math|Float|Min(Float) a 0.98))
{fly}
    (if (> a 1.0)
      (Variables|Default|SetFly false)
      (Variables|Default|SetT 0.0)
      (Variables|Default|SetNext (Math|Random|RandomFloatinRange :Min 4.5 :Max 8.0))
      (Audio|PlaySoundatLocation :Sound {g('Thud')} :Location (Math|Vector|MakeVector {g('TX0')} {g('TY0')} {g('TZ0')}) :VolumeMultiplier 0.8 :PitchMultiplier 1.8)
{land})
    (else
      (bind dist (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pl) (.x me)) (- (.y pl) (.y me)) 0.0)))
      (if (and (> {g('T')} {g('Next')}) (< dist 8500.0))
        (Variables|Default|SetFly true)
        (Variables|Default|SetT 0.0)
        (bind pv (Transformation|GetVelocity :self {PL}))
        (Variables|Default|SetDur (Math|Float|Clamp(Float) (/ dist 2600.0) 1.3 2.6))
        (Variables|Default|SetArc (+ 350.0 (* dist 0.1)))
{fire}
        (Audio|PlaySound2D :Sound {g('Whoosh')} :VolumeMultiplier 0.55 :PitchMultiplier 0.6)))))
"""
    r = TG.run(p, code, clear=True)
    S.editable(p, [f"A{k}" for k in range(NA)] + ["Whoosh", "Thud", "Next"], {"Next": 6.0})
    return str(r)[:200]

def archers_level():
    random.seed(5)
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Archers_"): E.destroy_actor(a)
    acls = EAL.load_asset(f"{WB}/BP_Archers").generated_class(); arrow = EAL.load_asset(f"{WB}/Archers/SM_Arrow")
    spots = [(3000, -5300), (5600, 5300), (7600, -5300), (9800, 5000), (-400, 4600)]
    out = []
    for i, (x, y) in enumerate(spots):
        z = M.ground_z(x, y) or 0.0
        c = E.spawn_actor_from_class(acls, V(x, y, z), unreal.Rotator()); c.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        c.set_actor_label(f"Archers_{i}"); c.set_folder_path("Art/War/Battle/Archers")
        for k in range(NA):
            a = E.spawn_actor_from_object(arrow, V(x, y, -15000 - i * 500 - k * 40)); a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            a.static_mesh_component.set_collision_profile_name("NoCollision"); a.set_actor_scale3d(V(1.3, 1.3, 1.3))
            a.set_actor_label(f"Archers_{i}_Arrow{k}"); a.set_folder_path("Art/War/Battle/Archers"); c.set_editor_property(f"A{k}", a)
        for j in range(3):
            yaw = math.degrees(math.atan2(-y, 4000 - x))
            S.soldier(f"Archers_{i}_Man{j}", x + random.uniform(-260, 260), y + random.uniform(-160, 160), z + 2, yaw, "CrouchLookAroundBow", "Art/War/Battle/Archers", sword=False)
        c.set_editor_property("Whoosh", EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Swing_5")); c.set_editor_property("Thud", EAL.load_asset(f"{R}/Audio/SFX/SFX_StoneImpact"))
        c.set_editor_property("Next", 3.0 + i * 1.3); out.append([x, y])
    return out

# ---------------------------------------------------------------- bigger field
def expand():
    random.seed(2027)
    out = {}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab == "Bound_War_1": a.set_actor_location(V(X1, 0, 400), False, False)
        if lab in ("Bound_War_2", "Bound_War_3"):
            l = a.get_actor_location(); a.set_actor_location(V((X1 - 900) / 2, l.y, 400), False, False); a.set_actor_scale3d(V((X1 + 900) / 100 + 2, 0.5, 10))
    # move the goal to the new far end
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("Goal_War_"):
            l = a.get_actor_location(); a.set_actor_location(V(l.x + 3900, l.y, l.z), False, False)
    # ground tiles in the new strip
    import tum_s391 as G
    rough = G.T.sms(f"{MS}/Rocky_Forest_Path_vefhef2ga") + G.T.sms(f"{MS}/Nordic_Beach_Rocky_Ground_ve3qdhmqx") + G.T.sms(f"{MS}/Nordic_Beach_Rocky_Ground_vf5pajccb") + G.T.sms(f"{MS}/Nordic_Beach_Rocky_Ground_ukoncdamw")
    nat = {}
    for m in rough:
        b = m.get_bounding_box(); nat[m.get_name()] = max(b.max.x - b.min.x, b.max.y - b.min.y)
    n = 0; x = 7100.0
    while x < X1 + 200:
        y = -4600.0
        while y < 4600:
            m = random.choice(rough)
            a = E.spawn_actor_from_object(m, V(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360)))
            s = random.uniform(0.9, 1.25); size = nat[m.get_name()] * s
            a.set_actor_scale3d(V(s, s, s * random.uniform(0.6, 0.9)))
            o, e = a.get_actor_bounds(False); l = a.get_actor_location()
            px, py = x + random.uniform(-50, 50), y + random.uniform(-50, 50)
            a.set_actor_location(V(l.x + px - o.x, l.y + py - o.y, l.z + 4 - (o.z + e.z) + e.z * 0.35), False, False)
            a.set_actor_enable_collision(False); a.static_mesh_component.set_cast_shadow(False)
            a.set_actor_label(f"GT3_{n}"); a.set_folder_path("Art/War/GroundTiles"); n += 1
            y += min(175.0, size * 0.7)
        x += 175.0
    out["tiles"] = n
    # cover boulders in the new strip
    boulders = S.sms(f"{MS}/Beach_Boulder_uisjbbis") + S.sms(f"{MS}/Nordic_Beach_Boulder_vcyqebjfa") + S.sms(f"{MS}/Limestone_Slab_ubxbadpda") if hasattr(S, "sms") else []
    if not boulders:
        import tum_s394 as K; boulders = K.sms(f"{MS}/Beach_Boulder_uisjbbis") + K.sms(f"{MS}/Nordic_Beach_Boulder_vcyqebjfa") + K.sms(f"{MS}/Limestone_Slab_ubxbadpda")
    obs = M.obstacles(); nb = 0; tries = 0
    while nb < 18 and tries < 4000:
        tries += 1
        x = random.uniform(7300, X1 - 400); y = random.uniform(-4200, 4200); size = random.uniform(170, 320)
        if any(M.inside(x, y, b, size * 0.7 + 120) for b in obs): continue
        a = E.spawn_actor_from_object(random.choice(boulders), V(0, 0, 0), unreal.Rotator(roll=random.uniform(-6, 6), pitch=random.uniform(-6, 6), yaw=random.uniform(0, 360)))
        o, e = a.get_actor_bounds(False); s = size / max(2 * max(e.x, e.y), 1); a.set_actor_scale3d(V(s, s, s * random.uniform(0.7, 1.1)))
        o, e = a.get_actor_bounds(False); l = a.get_actor_location()
        a.set_actor_location(V(l.x + x - o.x, l.y + y - o.y, l.z - (o.z - e.z) - 25), False, False)
        a.static_mesh_component.set_collision_profile_name("BlockAll"); a.set_actor_label(f"Cover_Boulder_X{nb}"); a.set_folder_path("Art/War/Cover")
        obs.append((a, o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y)); nb += 1
    out["boulders"] = nb
    # more fighting soldiers: copy duel pairs / wanderers into the new strip
    grp = [a for a in E.get_all_level_actors() if a.get_actor_label().startswith(("Duel2_", "Wander_")) and 2500 < a.get_actor_location().x < 7000]
    dup = E.duplicate_actors(grp, M.world(), V(3800, 0, 0))
    out["dup"] = len(dup)
    for a in dup:
        a.set_actor_label(a.get_actor_label() + "_X")
        for k in "ABC":
            try: a.set_editor_property(f"{k}X", a.get_editor_property(f"{k}X") + 3800.0)
            except Exception: pass
    return out

def run_b():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("catapult_bp", catapult_bp); step("catapults", catapults_level)
    L.save_current_level()
    return res
