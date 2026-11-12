# Systems batch: soft-fail respawn, Focus Cut, generic mover/trigger, reveal anchors, map routes
import unreal, importlib, traceback
import tum_graph as TG; importlib.reload(TG)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT, _BlueprintCache
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); R = "/Game/TUM"
CH, AN, FR, GI = f"{R}/Core/BP_TUMCharacter", f"{R}/Verbs/BP_AlignAnchor", f"{R}/Factory/BP_FactoryRoute", f"{R}/Core/BP_GameProgress"
MV, TR, RR = f"{R}/Props/BP_Mover", f"{R}/Core/BP_Trigger", f"{R}/Core/BP_RealRoomRoute"
GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
BLACK = "(Utilities|Struct|MakeLinearColor :R 0.0 :G 0.0 :B 0.0 :A 1.0)"
SILVER = "(Utilities|Struct|MakeLinearColor :R 0.82 :G 0.88 :B 1.0 :A 1.0)"
def show(tag, v, expr_hidden):
    return f'(for {v} (Actor|GetAllActorswithTag :Tag {tag}) (Rendering|SetActorHiddenInGame :self {v} :bNewHidden {expr_hidden}) (Collision|SetActorEnableCollision :self {v} :bNewActorEnableCollision (not {expr_hidden})))'
def bp(path):
    folder, name = path.rsplit("/", 1)
    return EAL.load_asset(path) if EAL.does_asset_exist(path) else BT.create(folder, name, unreal.Actor.static_class())
def editable(path, names, defaults):
    b = EAL.load_asset(path)
    for n in names: BEL.set_blueprint_variable_instance_editable(b, n, True)
    BEL.compile_blueprint(b); cdo = unreal.get_default_object(b.generated_class())
    for k, v in defaults.items(): cdo.set_editor_property(k, v)
    EAL.save_loaded_asset(b, False)
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]

def inputs():
    TG.ensure_vars(GI, [("GameEnded", "bool")])
    p = f"{R}/Core/IA_FocusCut"
    ia = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset("IA_FocusCut", f"{R}/Core", unreal.InputAction, unreal.InputAction_Factory())
    EAL.save_loaded_asset(ia)
    imc = EAL.load_asset("/Game/Input/IMC_Default")
    data = imc.get_editor_property("default_key_mappings"); maps = [m for m in data.get_editor_property("mappings") if m.get_editor_property("action") != ia]
    for key in ("F", "Gamepad_FaceButton_Top"):
        k = unreal.Key(); k.set_editor_property("key_name", key)
        m = unreal.EnhancedActionKeyMapping(); m.set_editor_property("action", ia); m.set_editor_property("key", k); maps.append(m)
    data.set_editor_property("mappings", maps); imc.set_editor_property("default_key_mappings", data); EAL.save_loaded_asset(imc, False)

def character():
    TG.ensure_vars(CH, [("KillZ", "float"), ("BestX", "float"), ("bFocusUnlocked", "bool"), ("bFocusReady", "bool")], objs=[("RespawnTarget", unreal.Actor.static_class())])
    code = f"""
(event Custom|DoBoost
  (if (and (Variables|Default|GetBoostUnlocked) (Variables|Default|GetCanBoost))
    (Variables|Default|SetCanBoost false)
    (Variables|Default|SetLastBoostTime (Utilities|Time|GetGameTimeinSeconds))
    (bind cm (Variables|Character|GetCharacterMovement))
    (if (Movement|IsFlying :self cm)
      (Class|CharacterMovementComponent|SetMaxFlySpeed :self cm :MaxFlySpeed 2800.0)
      (Utilities|FlowControl|Delay 0.7)
      (Class|CharacterMovementComponent|SetMaxFlySpeed :self cm :MaxFlySpeed 1200.0)
      (Utilities|FlowControl|Delay 0.5)
      (Variables|Default|SetCanBoost true)
      (else
        (bind f (Transformation|GetActorForwardVector))
        (Character|LaunchCharacter :LaunchVelocity (Math|Vector|MakeVector (* (.x f) (Variables|Default|GetBoostStrength)) (* (.y f) (Variables|Default|GetBoostStrength)) (Variables|Default|GetBoostLift)) :bXYOverride true :bZOverride true)
        (Utilities|FlowControl|Delay (Variables|Default|GetBoostCooldown))
        (Variables|Default|SetCanBoost true)))))

(event Custom|DoFocus
  (if (and (Variables|Default|GetFocusUnlocked) (Variables|Default|GetFocusReady))
    (Variables|Default|SetFocusReady false)
    (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager 0) :FromAlpha 0.6 :ToAlpha 0.0 :Duration 0.5 :Color {SILVER} :bHoldWhenFinished false)
    (for a (Actor|GetAllActorswithTag :Tag "FocusPause") (Actor|Tick|SetActorTickEnabled :self a :bEnabled false))
    (Utilities|FlowControl|Delay 12.0)
    (for a (Actor|GetAllActorswithTag :Tag "FocusPause") (Actor|Tick|SetActorTickEnabled :self a :bEnabled true))
    (Utilities|FlowControl|Delay 6.0)
    (Variables|Default|SetFocusReady true)))

(event Custom|Respawn
  (Variables|Default|SetBestX 99999999.0)
  (for c (Actor|GetAllActorswithTag :Tag "Checkpoint")
    (if (and (< (.x (Transformation|GetActorLocation :self c)) (+ (.x (Transformation|GetActorLocation)) 50.0)) (< (Transformation|GetDistanceTo :OtherActor c) (Variables|Default|GetBestX)))
      (Variables|Default|SetBestX (Transformation|GetDistanceTo :OtherActor c))
      (Variables|Default|SetRespawnTarget c)))
  (if (< (Variables|Default|GetBestX) 99999000.0)
    (Components|Movement|StopMovementImmediately :self (Variables|Character|GetCharacterMovement))
    (bind t (Transformation|GetActorLocation :self (Variables|Default|GetRespawnTarget)))
    (Transformation|SetActorLocation :NewLocation (Math|Vector|MakeVector (.x t) (.y t) (+ (.z t) 60.0)) :bTeleport true)
    (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager 0) :FromAlpha 1.0 :ToAlpha 0.0 :Duration 0.6 :Color {BLACK} :bHoldWhenFinished false)))

(event EventTick (DeltaSeconds)
  (if (< (.z (Transformation|GetActorLocation)) (Variables|Default|GetKillZ))
    (CallFunction|Respawn)))
"""
    r = TG.run(CH, code, events=["DoBoost", "DoFocus", "Respawn"], binds=[("IA_Boost", [("Started", "DoBoost")]), ("IA_FocusCut", [("Started", "DoFocus")])], clear=True)
    b = EAL.load_asset(CH); cdo = unreal.get_default_object(b.generated_class())
    cdo.set_editor_property("KillZ", -400.0); cdo.set_editor_property("bFocusReady", True); cdo.set_editor_property("bFocusUnlocked", False)
    EAL.save_loaded_asset(b, False); return r

def mover():
    bp(MV)
    TG.ensure_vars(MV, [(n, "float") for n in ("AmpX", "AmpY", "AmpZ", "Speed", "Phase", "KillRadius", "T", "BaseX", "BaseY", "BaseZ")] + [("bStartDisabled", "bool")])
    g = lambda n: f"(Variables|Default|Get{n})"
    code = f"""
(event EventBeginPlay
  (bind l (Transformation|GetActorLocation))
  (Variables|Default|SetBaseX (.x l))
  (Variables|Default|SetBaseY (.y l))
  (Variables|Default|SetBaseZ (.z l))
  (Actor|Tick|SetActorTickEnabled :bEnabled (not {g('StartDisabled')})))

(event EventTick (DeltaSeconds)
  (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
  (bind s (Math|Trig|Sin(Radians) (+ (* {g('T')} {g('Speed')}) {g('Phase')})))
  (Transformation|SetActorLocation :NewLocation (Math|Vector|MakeVector (+ {g('BaseX')} (* {g('AmpX')} s)) (+ {g('BaseY')} (* {g('AmpY')} s)) (+ {g('BaseZ')} (* {g('AmpZ')} s))) :bTeleport true)
  (if (and (> {g('KillRadius')} 0.0) (< (Transformation|GetDistanceTo :OtherActor (Game|GetPlayerCharacter 0)) {g('KillRadius')}))
    (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object (Game|GetPlayerCharacter 0))
      (:then (Class|BPTUMCharacter|Respawn :self ch))
      (:CastFailed))))
"""
    r = TG.run(MV, code, clear=True)
    editable(MV, ["AmpX", "AmpY", "AmpZ", "Speed", "Phase", "KillRadius", "bStartDisabled"], {"Speed": 1.0, "KillRadius": 0.0})
    return r

def trigger():
    bp(TR)
    TG.ensure_vars(TR, [("Radius", "float"), ("ShowTag", "name"), ("HideTag", "name"), ("HideTag2", "name"), ("Flag", "int"), ("bOpenMap", "bool"), ("TargetMap", "name"), ("bUsed", "bool"), ("bStartDisabled", "bool")])
    g = lambda n: f"(Variables|Default|Get{n})"
    def setflag(var, pin, n): return f"(Class|BPGameProgress|Set{var} :self gi :{pin} (or (Class|BPGameProgress|Get{var} :self gi) (== {g('Flag')} {n})))"
    code = f"""
(event EventBeginPlay
  (Actor|Tick|SetActorTickEnabled :bEnabled (not {g('StartDisabled')})))

(event EventTick (DeltaSeconds)
  (bind dist (Transformation|GetDistanceTo :OtherActor (Game|GetPlayerCharacter 0)))
  (if (and (not {g('Used')}) (and (> dist 1.0) (< dist {g('Radius')})))
    (Variables|Default|SetUsed true)
    (CallFunction|Fire)))

(event Custom|Fire
  (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager 0) :FromAlpha 0.5 :ToAlpha 0.0 :Duration 0.35 :Color {SILVER} :bHoldWhenFinished false)
  (for a (Actor|GetAllActorswithTag :Tag {g('ShowTag')})
    (Rendering|SetActorHiddenInGame :self a :bNewHidden false)
    (Collision|SetActorEnableCollision :self a :bNewActorEnableCollision true)
    (Actor|Tick|SetActorTickEnabled :self a :bEnabled true))
  (for a (Actor|GetAllActorswithTag :Tag {g('HideTag')})
    (Rendering|SetActorHiddenInGame :self a :bNewHidden true)
    (Collision|SetActorEnableCollision :self a :bNewActorEnableCollision false)
    (Actor|Tick|SetActorTickEnabled :self a :bEnabled false))
  (for a (Actor|GetAllActorswithTag :Tag {g('HideTag2')})
    (Rendering|SetActorHiddenInGame :self a :bNewHidden true)
    (Collision|SetActorEnableCollision :self a :bNewActorEnableCollision false))
  (if {g('OpenMap')}
    (bind gi {GP}
      (:then
        {setflag('DragonDone', 'DragonDone', 1)}
        {setflag('WarDone', 'WarDone', 2)}
        {setflag('CliffDone', 'CliffDone', 3)}
        {setflag('HasFocusCut', 'bHasFocusCut', 3)}
        {setflag('GameEnded', 'GameEnded', 4)}
        (Input|DisableInput :self (Game|GetPlayerCharacter 0) :PlayerController (Game|GetPlayerController 0))
        (Utilities|FlowControl|Delay 0.5)
        (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager 0) :FromAlpha 0.0 :ToAlpha 1.0 :Duration 1.0 :Color {BLACK} :bHoldWhenFinished true)
        (Utilities|FlowControl|Delay 1.1)
        (Game|OpenLevel(byName) :LevelName {g('TargetMap')}))
      (:CastFailed))))
"""
    r = TG.run(TR, code, events=["Fire"], clear=True)
    editable(TR, ["Radius", "ShowTag", "HideTag", "HideTag2", "Flag", "bOpenMap", "TargetMap", "bStartDisabled"], {"Radius": 200.0, "TargetMap": "M_FactoryHub"})
    return r

def anchor():
    TG.ensure_vars(AN, [("bRevealOnly", "bool"), ("RevealTag", "name"), ("RevealTime", "float"), ("bSaveReturn", "bool")])
    code = f"""
(event EventTick (DeltaSeconds)
  (if (not (Variables|Default|GetUsed))
    (bind p (Game|GetPlayerCharacter 0))
    (bind pcm (Game|GetPlayerCameraManager 0))
    (bind cl (Camera|GetCameraLocation :self pcm))
    (bind fw (Math|Vector|GetForwardVector :InRot (Camera|GetCameraRotation :self pcm)))
    (bind tl (Transformation|GetActorLocation :self (Variables|Default|GetAlignTarget)))
    (bind dx (- (.x tl) (.x cl)))
    (bind dy (- (.y tl) (.y cl)))
    (bind dz (- (.z tl) (.z cl)))
    (bind dot (/ (+ (+ (* dx (.x fw)) (* dy (.y fw))) (* dz (.z fw))) (Math|Float|Sqrt (+ (+ (* dx dx) (* dy dy)) (* dz dz)))))
    (if (and (< (Transformation|GetDistanceTo :OtherActor p) (Variables|Default|GetRadius)) (> dot (Variables|Default|GetMinDot)))
      (Variables|Default|SetHold (+ (Variables|Default|GetHold) DeltaSeconds))
      (if (> (Variables|Default|GetHold) 0.35)
        (Variables|Default|SetUsed true)
        (CallFunction|Fire))
      (else
        (Variables|Default|SetHold 0.0)))))

(event Custom|Fire
  (bind pcm (Game|GetPlayerCameraManager 0))
  (bind p (Game|GetPlayerCharacter 0))
  (CameraFades|StartCameraFade :self pcm :FromAlpha 0.9 :ToAlpha 0.0 :Duration 0.35 :Color {SILVER} :bHoldWhenFinished false)
  (if (Variables|Default|GetRevealOnly)
    {show('(Variables|Default|GetRevealTag)', 'a', 'false')}
    (Utilities|FlowControl|Delay (Variables|Default|GetRevealTime))
    {show('(Variables|Default|GetRevealTag)', 'b', 'true')}
    (Variables|Default|SetHold 0.0)
    (Variables|Default|SetUsed false)
    (else
      (Input|DisableInput :self p :PlayerController (Game|GetPlayerController 0))
      (bind gi {GP}
        (:then
          (Class|BPGameProgress|SetReturnTransform :self gi :ReturnTransform (Transformation|GetActorTransform :self p))
          (Class|BPGameProgress|SetHasReturn :self gi :bHasReturn (Variables|Default|GetSaveReturn))
          (Utilities|FlowControl|Delay 0.4)
          (CameraFades|StartCameraFade :self pcm :FromAlpha 0.0 :ToAlpha 1.0 :Duration 0.8 :Color {BLACK} :bHoldWhenFinished true)
          (Utilities|FlowControl|Delay 0.9)
          (Game|OpenLevel(byName) :LevelName (Variables|Default|GetTargetMap)))
        (:CastFailed)))))
"""
    r = TG.run(AN, code, events=["Fire"], clear=True)
    editable(AN, ["TargetMap", "AlignTarget", "Radius", "MinDot", "bRevealOnly", "RevealTag", "RevealTime", "bSaveReturn"], {"bSaveReturn": True, "RevealTime": 10.0, "Radius": 320.0, "MinDot": 0.996})
    return r

def factory():
    code = f"""
(event EventBeginPlay
  (Utilities|FlowControl|Delay 0.1)
  (bind p (Game|GetPlayerCharacter 0))
  (bind gi {GP}
    (:then
      (bind dragon (Class|BPGameProgress|GetDragonDone :self gi))
      (bind war (Class|BPGameProgress|GetWarDone :self gi))
      (bind cliff (Class|BPGameProgress|GetCliffDone :self gi))
      {show('"DragonLift"', 'a', '(not dragon)')}
      {show('"WarBridge"', 'b', '(not war)')}
      (for c (Actor|GetAllActorswithTag :Tag "CutAnchor_Dragon") (Actor|Tick|SetActorTickEnabled :self c :bEnabled (not dragon)))
      (for d (Actor|GetAllActorswithTag :Tag "CutAnchor_War") (Actor|Tick|SetActorTickEnabled :self d :bEnabled (not war)))
      (for e (Actor|GetAllActorswithTag :Tag "CutAnchor_Cliff") (Actor|Tick|SetActorTickEnabled :self e :bEnabled (not cliff)))
      (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object p)
        (:then
          (Class|BPTUMCharacter|SetBoostUnlocked :self ch :bBoostUnlocked (Class|BPGameProgress|GetHasBoost :self gi))
          (Class|BPTUMCharacter|SetFocusUnlocked :self ch :bFocusUnlocked (Class|BPGameProgress|GetHasFocusCut :self gi))
          (Class|BPTUMCharacter|SetFocusReady :self ch :bFocusReady true)
          (if (Class|BPGameProgress|GetHasReturn :self gi)
            (Transformation|SetActorTransform :self p :NewTransform (Class|BPGameProgress|GetReturnTransform :self gi))
            (Class|BPGameProgress|SetHasReturn :self gi :bHasReturn false)))
        (:CastFailed)))
    (:CastFailed)))
"""
    return TG.run(FR, code, clear=True)

def realroom():
    bp(RR)
    code = f"""
(event EventBeginPlay
  (Utilities|FlowControl|Delay 0.1)
  (bind gi {GP}
    (:then
      (bind ended (Class|BPGameProgress|GetGameEnded :self gi))
      {show('"Ending"', 'a', '(not ended)')}
      {show('"Intro"', 'b', 'ended')}
      (for c (Actor|GetAllActorswithTag :Tag "CutAnchor_Factory") (Actor|Tick|SetActorTickEnabled :self c :bEnabled (not ended))))
    (:CastFailed)))
"""
    return TG.run(RR, code, clear=True)

STEPS = []
def run_all():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    for n, fn in STEPS: step(n, fn)
    res["status"] = {p.split("/")[-1]: str(EAL.load_asset(p).get_editor_property("status")) for p in (CH, MV, TR, AN, FR, RR) if EAL.does_asset_exist(p)}
    return res
