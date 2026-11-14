# Cavalry: mounted knights that wait in the fog, then charge in a straight line at where you are and ride on past.
# If one reaches you: you are thrown, lose health and fall to the ground (fall anim, no control for a moment).
import unreal, importlib, traceback, random, math
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
import tum_s364b as S; importlib.reload(S)
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
HS = 0.55
def mesh(var): return f"(Class|SkeletalMeshActor|GetSkeletalMeshComponent :self {g(var)})"
def play(var, anim, loop="true"): return f"(Components|Animation|PlayAnimation :self {mesh(var)} :NewAnimToPlay {anim} :bLooping {loop})"

def cavalry_bp():
    p = f"{WB}/BP_Cavalry"
    if not EAL.does_asset_exist(p):
        from editor_toolset.toolsets.blueprint import BlueprintTools as BT
        BT.create(WB, "BP_Cavalry", unreal.Actor.static_class())
    TG.ensure_vars(p, [(n, "float") for n in ("T", "Wait", "DX", "DY", "TX", "TY", "Speed", "Run")] + [("State", "int"), ("bHit", "bool")],
                   objs=[("Horse", unreal.SkeletalMeshActor.static_class()), ("Rider", unreal.SkeletalMeshActor.static_class()), ("Gallop", unreal.AnimSequence.static_class()),
                         ("Idle", unreal.AnimSequence.static_class()), ("FallAnim", unreal.AnimSequence.static_class()), ("Hoof", unreal.SoundBase.static_class()), ("Thud", unreal.SoundBase.static_class())])
    trace = f"(Collision|LineTraceByChannel :Start (Math|Vector|MakeVector (+ (.x me) (* {g('DX')} 120.0)) (+ (.y me) (* {g('DY')} 120.0)) (+ (.z me) 90.0)) :End (Math|Vector|MakeVector (+ (.x me) (* {g('DX')} 420.0)) (+ (.y me) (* {g('DY')} 420.0)) (+ (.z me) 90.0)))"
    code = f"""
(event EventBeginPlay
  (Variables|Default|SetState 0)
  (Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 1.5 :Max 6.0)))

(event Custom|KnockDown
  (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object {PL})
    (:then
      (Input|DisableInput :self ch :PlayerController (Game|GetPlayerController 0))
      (Components|Animation|PlayAnimation :self (Class|Character|GetMesh :self ch) :NewAnimToPlay {g('FallAnim')} :bLooping false)
      (Utilities|FlowControl|Delay 1.7)
      (Components|Animation|SetAnimationMode :self (Class|Character|GetMesh :self ch) :InAnimationMode "AnimationBlueprint")
      (Input|EnableInput :self ch :PlayerController (Game|GetPlayerController 0)))
    (:CastFailed)))

(event EventTick (DeltaSeconds)
  (bind me (Transformation|GetActorLocation))
  (bind pl (Transformation|GetActorLocation :self {PL}))
  (bind dpx (- (.x pl) (.x me)))
  (bind dpy (- (.y pl) (.y me)))
  (bind dp (Math|Vector|VectorLength (Math|Vector|MakeVector dpx dpy 0.0)))
  (if (== {g('State')} 0)
    (Variables|Default|SetWait (- {g('Wait')} DeltaSeconds))
    (Transformation|SetActorRotation :NewRotation (Math|Interpolation|RInterpTo :Current (Transformation|GetActorRotation) :Target (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (Math|Trig|Atan2(Degrees) dpy dpx)) :DeltaTime DeltaSeconds :InterpSpeed 2.0) :bTeleportPhysics true)
    (if (and (< {g('Wait')} 0.0) (< dp 4800.0))
      (Variables|Default|SetState 1)
      (Variables|Default|SetRun 0.0)
      (Variables|Default|SetHit false)
      (Variables|Default|SetDX (/ dpx (+ dp 1.0)))
      (Variables|Default|SetDY (/ dpy (+ dp 1.0)))
      (Variables|Default|SetTX (+ (.x pl) (* {g('DX')} 2200.0)))
      (Variables|Default|SetTY (+ (.y pl) (* {g('DY')} 2200.0)))
      (Transformation|SetActorRotation :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (Math|Trig|Atan2(Degrees) dpy dpx)) :bTeleportPhysics true)
      {play('Horse', g('Gallop'))}
      (Audio|PlaySoundatLocation :Sound {g('Hoof')} :Location me :VolumeMultiplier 1.2 :PitchMultiplier 0.7)))
  (if (== {g('State')} 1)
    (bind step (* {g('Speed')} DeltaSeconds))
    (Variables|Default|SetRun (+ {g('Run')} step))
    (Transformation|SetActorLocation :NewLocation (Math|Vector|MakeVector (+ (.x me) (* {g('DX')} step)) (+ (.y me) (* {g('DY')} step)) (.z me)) :bTeleport true)
    (if (or (or {trace} (> {g('Run')} 7500.0)) (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- {g('TX')} (.x me)) (- {g('TY')} (.y me)) 0.0)) 150.0))
      (Variables|Default|SetState 0)
      (Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 2.5 :Max 5.5))
      {play('Horse', g('Idle'))})
    (if (and (< dp 210.0) (not {g('Hit')}))
      (Variables|Default|SetHit true)
      (Audio|PlaySoundatLocation :Sound {g('Thud')} :Location pl :VolumeMultiplier 1.3 :PitchMultiplier 0.8)
      (CallFunction|KnockDown)
      (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object {PL})
        (:then
          (Character|LaunchCharacter :self ch :LaunchVelocity (Math|Vector|MakeVector (* {g('DX')} 950.0) (* {g('DY')} 950.0) 480.0) :bXYOverride true :bZOverride true)
          (Class|BPTUMCharacter|SetHealth :self ch :Health (- (Class|BPTUMCharacter|GetHealth :self ch) 28.0))
          (Class|BPTUMCharacter|SetLastHit :self ch :LastHit (Utilities|Time|GetGameTimeinSeconds)))
        (:CastFailed)))))
"""
    r = TG.run(p, code, events=["KnockDown"], clear=True)
    S.editable(p, ["Horse", "Rider", "Gallop", "Idle", "FallAnim", "Hoof", "Thud", "Speed"], {"Speed": 1150.0})
    return str(r)[:200]

def place():
    random.seed(321)
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Cavalry_"): E.destroy_actor(a)
    ccls = EAL.load_asset(f"{WB}/BP_Cavalry").generated_class()
    looks = [("Brown", "Horse"), ("White", "Horse_White")]
    spots = [(2400, -3800), (3800, 3900), (5200, -2600), (6600, 3400), (8000, -3900), (9200, 2600), (1500, 3600)]
    out = []
    for i, (x, y) in enumerate(spots):
        col, nm = looks[i % 2]; base = f"{WB}/Horse/{col}"
        z = M.ground_z(x, y) or 0.0
        c = E.spawn_actor_from_class(ccls, V(x, y, z), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360))); c.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        h = E.spawn_actor_from_class(unreal.SkeletalMeshActor, V(x, y, z)); hc = h.skeletal_mesh_component
        hc.set_skeletal_mesh_asset(EAL.load_asset(f"{base}/{nm}")); hc.set_mobility(unreal.ComponentMobility.MOVABLE)
        hc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        d = unreal.SingleAnimationPlayData(); d.set_editor_property("anim_to_play", EAL.load_asset(f"{base}/{nm}Idle")); d.set_editor_property("saved_looping", True); d.set_editor_property("saved_playing", True)
        hc.set_editor_property("animation_data", d); hc.set_collision_profile_name("NoCollision"); h.set_actor_enable_collision(False)
        h.set_actor_scale3d(V(HS, HS, HS))
        h.attach_to_actor(c, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        h.root_component.set_relative_location(V(0, 0, 0), False, False); h.root_component.set_relative_rotation(unreal.Rotator(roll=0, pitch=0, yaw=-90), False, False)
        rider = S.soldier(f"Cavalry_{i}_Rider", x, y, z, 0, "CrouchLookAroundBow", "Art/War/Battle/Cavalry", pos=0.35)
        rc = rider.skeletal_mesh_component; dd = rc.get_editor_property("animation_data"); dd.set_editor_property("saved_playing", False); rc.set_editor_property("animation_data", dd)
        rider.attach_to_actor(c, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        rider.root_component.set_relative_location(V(-15, 0, 118), False, False); rider.root_component.set_relative_rotation(unreal.Rotator(roll=0, pitch=0, yaw=-90), False, False)
        h.set_actor_label(f"Cavalry_{i}_Horse"); c.set_actor_label(f"Cavalry_{i}")
        for a_ in (h, c): a_.set_folder_path("Art/War/Battle/Cavalry")
        c.set_editor_property("Horse", h); c.set_editor_property("Rider", rider)
        c.set_editor_property("Gallop", EAL.load_asset(f"{base}/{nm}Gallop")); c.set_editor_property("Idle", EAL.load_asset(f"{base}/{nm}Idle"))
        c.set_editor_property("FallAnim", EAL.load_asset("/Game/Characters/Mannequins/Anims/Death/MM_Death_Back_01"))
        c.set_editor_property("Hoof", EAL.load_asset(f"{R}/Audio/SFX/SFX_StoneImpact")); c.set_editor_property("Thud", EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Clash_7"))
        c.set_editor_property("Speed", random.uniform(1050.0, 1250.0))
        out.append([x, y])
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("bp", cavalry_bp); step("place", place)
    return res
