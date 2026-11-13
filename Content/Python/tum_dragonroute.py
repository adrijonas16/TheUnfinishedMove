import unreal, importlib, traceback
import tum_graph as TG; importlib.reload(TG)
EAL = unreal.EditorAssetLibrary
res = {"ok": [], "err": {}}
CH = "/Game/TUM/Core/BP_TUMCharacter"; AN = "/Game/TUM/Verbs/BP_AlignAnchor"; FR = "/Game/TUM/Factory/BP_FactoryRoute"; DR = "/Game/TUM/Cuts/Dragon/BP_DragonRoute"
GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
BLACK = "(Utilities|Struct|MakeLinearColor :R 0.0 :G 0.0 :B 0.0 :A 1.0)"
SILVER = "(Utilities|Struct|MakeLinearColor :R 0.82 :G 0.88 :B 1.0 :A 1.0)"
def step(name, fn):
    try: fn(); res["ok"].append(name)
    except Exception: res["err"][name] = traceback.format_exc()[-1200:]
# ---------- character: Boost works on foot (launch) and on the dragon (flying speed burst)
def dragon():
    TG.ensure_vars(DR, [("Gate1X", "float"), ("Gate2X", "float"), ("Gate3X", "float"), ("NextGateX", "float"), ("GateIndex", "int"), ("EndX", "float"), ("bFinished", "bool"), ("bStarted", "bool")],
                   objs=[("Rider", EAL.load_asset(CH).generated_class())])
    code = f"""
(event EventBeginPlay
  (Utilities|FlowControl|Delay 0.05)
  (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object (Game|GetPlayerCharacter 0))
    (:then
      (Variables|Default|SetRider ch)
      (for b (Actor|GetAllActorswithTag :Tag "DragonBody")
        (Transformation|AttachActorToActor :self b :ParentActor ch :LocationRule "KeepWorld" :RotationRule "KeepWorld" :ScaleRule "KeepWorld"))
      (Class|BPTUMCharacter|SetBoostUnlocked :self ch :bBoostUnlocked true)
      (bind cm (Class|Character|GetCharacterMovement :self ch))
      (Class|CharacterMovementComponent|SetGravityScale :self cm :GravityScale 0.0)
      (Class|CharacterMovementComponent|SetMaxFlySpeed :self cm :MaxFlySpeed 850.0)
      (Pawn|Components|CharacterMovement|SetMovementMode :self cm :NewMovementMode "MOVE_Flying")
      (Variables|Default|SetNextGateX (Variables|Default|GetGate1X))
      (Variables|Default|SetGateIndex 0)
      (Variables|Default|SetStarted true))
    (:CastFailed)))

(event EventTick (DeltaSeconds)
  (bind ch (Variables|Default|GetRider))
  (if (and (Variables|Default|GetStarted) (not (Variables|Default|GetFinished)))
    (Pawn|Input|AddMovementInput :self ch :WorldDirection (Math|Vector|MakeVector 1.0 0.0 0.0) :ScaleValue 1.0)
    (bind l (Transformation|GetActorLocation :self ch))
    (if (< (.z l) (- 1950.0 (* (.x l) -0.0)))
      (if (< (.x l) 500.0)
        (Pawn|Input|AddMovementInput :self ch :WorldDirection (Math|Vector|MakeVector 0.0 0.0 1.0) :ScaleValue 0.62)))
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
    res["dragon"] = TG.run(DR, code, events=["FinishCut"], clear=True)
    cdo = unreal.get_default_object(EAL.load_asset(DR).generated_class())
    for k, v in [("Gate1X", 4000.0), ("Gate2X", 7500.0), ("Gate3X", 10500.0), ("EndX", 12200.0)]: cdo.set_editor_property(k, v)
    EAL.save_loaded_asset(EAL.load_asset(DR), False)

def run():
    step("dragon", dragon)
    return res
