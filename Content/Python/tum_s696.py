# Dragon flight v2 (wing beat scrubbed from the Fab clip, which is not a flight loop): you fly a dragon, not walk in the air. The dragon keeps its nose along the canyon, banks into turns
# (camera rolls with it), lifts/drops its nose when climbing/diving, glides with inertia; look up/down to climb/dive.
import unreal, importlib, traceback, re
import tum_s666 as Q
import tum_s612 as T612
import tum_graph as TG
import tum_s699 as SEAT
importlib.reload(SEAT)
OFFX, OFFZ = SEAT.OFFX, SEAT.OFFZ
FLAP = 2.856   # rad/s: the clip is scrubbed 0.02..0.85 s and back (wings flat -> down -> up), one full pass every 2.2 s
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
DR = "/Game/TUM/Cuts/Dragon/BP_DragonRoute"; CH = "/Game/TUM/Core/BP_TUMCharacter"
GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
SILVER = "(Utilities|Struct|MakeLinearColor :R 0.82 :G 0.88 :B 1.0 :A 1.0)"
g = lambda n: f"(Variables|Default|Get{n})"
def vec(x, y, z): return f"(Math|Vector|MakeVector {x} {y} {z})"
OPT = ["      (Class|CharacterMovementComponent|SetBrakingDecelerationFlying :self cm :BrakingDecelerationFlying 420.0)",
       "      (Class|CharacterMovementComponent|SetMaxAcceleration :self cm :MaxAcceleration 1250.0)"]
def code(opt):
    rb = f"(* {g('Bank')} 0.017453)"; rp = f"(* {g('Nose')} 0.017453)"
    # seat offset (dragon origin - rider) turned with the dragon: nose pitch first, then bank (same order as the actor rotation)
    zt = f"(+ (* {g('OffX')} (Math|Trig|Sin(Radians) {rp})) (* {g('OffZ')} (Math|Trig|Cos(Radians) {rp})))"
    ox = f"(- (* {g('OffX')} (Math|Trig|Cos(Radians) {rp})) (* {g('OffZ')} (Math|Trig|Sin(Radians) {rp})))"
    y1 = f"(* {zt} (Math|Trig|Sin(Radians) {rb}))"; oz = f"(* {zt} (Math|Trig|Cos(Radians) {rb}))"
    return f"""
(event EventBeginPlay
  (Utilities|FlowControl|Delay 0.05)
  (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object (Game|GetPlayerCharacter 0))
    (:then
      (Variables|Default|SetRider ch)
      (for b (Actor|GetAllActorswithTag :Tag "DragonBody")
        (Variables|Default|SetDragonRef b)
        (Variables|Default|SetOffX {OFFX})
        (Variables|Default|SetOffZ {OFFZ})
        (Transformation|AttachActorToActor :self b :ParentActor ch :LocationRule "KeepWorld" :RotationRule "KeepWorld" :ScaleRule "KeepWorld")
        (bind sk (Utilities|Casting|CastToSkeletalMeshActor :Object b)
          (:then
            (Variables|Default|SetDragonSkel (Class|SkeletalMeshActor|GetSkeletalMeshComponent :self sk))
            (Components|Animation|SetPlayRate :self (Variables|Default|GetDragonSkel) :Rate 0.0))
          (:CastFailed)))
      (Class|BPTUMCharacter|SetBoostUnlocked :self ch :bBoostUnlocked true)
      (bind cm (Class|Character|GetCharacterMovement :self ch))
      (Class|CharacterMovementComponent|SetGravityScale :self cm :GravityScale 0.0)
      (Class|CharacterMovementComponent|SetMaxFlySpeed :self cm :MaxFlySpeed 850.0)
      (Pawn|Components|CharacterMovement|SetMovementMode :self cm :NewMovementMode "MOVE_Flying")
{chr(10).join(opt)}
      (Variables|Default|SetNextGateX (Variables|Default|GetGate1X))
      (Variables|Default|SetGateIndex 0)
      (Variables|Default|SetStarted true))
    (:CastFailed)))

(event EventTick (DeltaSeconds)
  (bind ch (Variables|Default|GetRider))
  (if (and (Variables|Default|GetStarted) (not (Variables|Default|GetFinished)))
    (Pawn|Input|AddMovementInput :self ch :WorldDirection (Math|Vector|MakeVector 1.0 0.0 0.0) :ScaleValue 1.6)
    (bind l (Transformation|GetActorLocation :self ch))
    (bind v (Transformation|GetVelocity :self ch))
    (if (< (.z l) 1950.0)
      (if (< (.x l) 500.0)
        (Pawn|Input|AddMovementInput :self ch :WorldDirection (Math|Vector|MakeVector 0.0 0.0 1.0) :ScaleValue 0.62)))
    (if (> (.y l) 700.0)
      (Pawn|Input|AddMovementInput :self ch :WorldDirection (Math|Vector|MakeVector 0.0 -1.0 0.0) :ScaleValue 1.25))
    (if (< (.y l) -700.0)
      (Pawn|Input|AddMovementInput :self ch :WorldDirection (Math|Vector|MakeVector 0.0 1.0 0.0) :ScaleValue 1.25))
    (if (> (.x l) 500.0)
      (bind (crr crp cry) (Math|Rotator|BreakRotator (Pawn|GetControlRotation :self ch)))
      (Pawn|Input|AddMovementInput :self ch :WorldDirection (Math|Vector|MakeVector 0.0 0.0 1.0) :ScaleValue (Math|Float|Clamp(Float) (/ (Math|Rotator|NormalizeAxis crp) 28.0) -1.0 1.0)))
    (Variables|Default|SetBank (Math|Interpolation|FInterpTo :Current {g('Bank')} :Target (* (Math|Float|Clamp(Float) (/ (.y v) 600.0) -1.0 1.0) 32.0) :DeltaTime DeltaSeconds :InterpSpeed 4.5))
    (Variables|Default|SetNose (Math|Interpolation|FInterpTo :Current {g('Nose')} :Target (* (Math|Float|Clamp(Float) (/ (.z v) 500.0) -1.0 1.0) 15.0) :DeltaTime DeltaSeconds :InterpSpeed 4.0))
    (Transformation|SetActorLocationAndRotation :self {g('DragonRef')} :NewLocation {vec(f"(+ (.x l) {ox})", f"(+ (.y l) {y1})", f"(+ (.z l) {oz})")} :NewRotation (Math|Rotator|MakeRotator :Roll (- 0.0 {g('Nose')}) :Pitch {g('Bank')} :Yaw -90.0) :bTeleport true)
    (Components|Animation|SetPosition :self (Variables|Default|GetDragonSkel) :InPos (- 0.435 (* 0.415 (Math|Trig|Cos(Radians) (* (Utilities|Time|GetGameTimeinSeconds) {FLAP})))) :bFireNotifies false)
    (Transformation|SetRelativeRotation :self (Class|BPThirdPersonCharacter|GetFollowCamera :self ch) :NewRotation (Math|Rotator|MakeRotator :Roll (* {g('Bank')} 0.45) :Pitch 0.0 :Yaw 0.0))
    (if (> (.x l) (Variables|Default|GetNextGateX))
      (if (< (- (Utilities|Time|GetGameTimeinSeconds) (Class|BPTUMCharacter|GetLastBoostTime :self ch)) 1.0)
        (Variables|Default|SetGateIndex (+ (Variables|Default|GetGateIndex) 1))
        (if (== (Variables|Default|GetGateIndex) 1)
          (Variables|Default|SetNextGateX (Variables|Default|GetGate2X))
          (else
            (if (== (Variables|Default|GetGateIndex) 2)
              (Variables|Default|SetNextGateX (Variables|Default|GetGate3X))
              (else (Variables|Default|SetNextGateX 9999999.0)))))
        (else
          (Transformation|SetActorLocation :self ch :NewLocation (Math|Vector|MakeVector (- (Variables|Default|GetNextGateX) 1100.0) (.y l) (.z l)) :bTeleport true)
          (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager 0) :FromAlpha 0.7 :ToAlpha 0.0 :Duration 0.4 :Color {SILVER} :bHoldWhenFinished false))))
    (if (> (.x l) (Variables|Default|GetEndX))
      (Variables|Default|SetFinished true)
      (CallFunction|FinishCut))))

(event Custom|FinishCut
  (bind pcm (Game|GetPlayerCameraManager 0))
  (CameraFades|StartCameraFade :self pcm :FromAlpha 0.0 :ToAlpha 1.0 :Duration 0.8 :Color {SILVER} :bHoldWhenFinished true)
  (bind gi {GP}
    (:then
      (Class|BPGameProgress|SetDragonDone :self gi :DragonDone true)
      (Class|BPGameProgress|SetHasBoost :self gi :bHasBoost true)
      (Utilities|FlowControl|Delay 1.0)
      (Game|OpenLevel(byName) :LevelName "M_FactoryHub"))
    (:CastFailed)))
"""
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    out = {}
    TG.ensure_vars(DR, [(n, "float") for n in ("OffX", "OffZ", "Bank", "Nose")], objs=[("DragonRef", unreal.Actor.static_class()), ("DragonSkel", unreal.SkeletalMeshComponent.static_class())])
    bp = EAL.load_asset(DR); graph = BEL.find_event_graph(bp)
    opt = []
    for line in OPT:
        if not TG.check_ids(graph, T612._resolve(DR, line)): opt.append(line)
    out["optional_used"] = len(opt)
    c = T612._resolve(DR, code(opt)); miss = TG.check_ids(graph, c); out["missing"] = miss; out["fixed"] = dict(T612.res.get("fixed", {}))
    if miss or TG.balance(c): out["aborted"] = True; return out
    try: out["run"] = Q.patched(lambda: str(TG.run(DR, c, events=["FinishCut"], clear=True))[:300])
    except Exception: out["err"] = traceback.format_exc()[-1500:]
    return out
