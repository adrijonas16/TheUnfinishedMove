# Intro: press E at the chair to sit (animated), press E again to pick up the earbuds and put them in (animated), music + slow camera drift into the factory
import unreal, importlib, traceback, math
import tum_graph as TG; importlib.reload(TG)
import tum_anim as TA; importlib.reload(TA)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); BEL = unreal.BlueprintEditorLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; DIR = f"{R}/Core/BP_IntroDirector"; ANIMS = f"{R}/Anims"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a

# ---------------- animations ----------------
SIT = {"thigh_l": (0, 0, -90), "thigh_r": (0, 0, -90), "calf_l": (0, 0, 92), "calf_r": (0, 0, 92), "foot_l": (0, 0, -8), "foot_r": (0, 0, -8),
       "spine_02": (0, 0, 0), "upperarm_l": (0, -10, 38), "upperarm_r": (0, -10, 38), "lowerarm_l": (0, 0, -45), "lowerarm_r": (0, 0, -45)}
DOWN = {"pelvis": (0, 0, -45)}
def anims():
    st = {}
    TA.make("A_SitDown", [(0.0, {}, {}), (0.35, {"thigh_l": (0, 0, -30), "thigh_r": (0, 0, -30), "calf_l": (0, 0, 35), "calf_r": (0, 0, 35)}, {"pelvis": (0, 0, -12)}),
                         (1.3, SIT, DOWN)], 1.3)
    breathe = dict(SIT, spine_03=(0, 0, 0)); b2 = dict(SIT, head=(0, 0, 4))
    TA.make("A_SitIdle", [(0.0, SIT, DOWN), (2.0, b2, DOWN), (4.0, SIT, DOWN)], 4.0)
    reach = dict(SIT, upperarm_r=(0, -5, 70), lowerarm_r=(0, 0, -25), head=(0, 0, 10))
    grab = dict(reach, hand_r=(0, 0, 20))
    ear_r = dict(SIT, upperarm_r=(0, 40, 30), lowerarm_r=(0, 0, -128), hand_r=(0, 0, 10), head=(0, 0, -4))
    both = dict(ear_r, upperarm_l=(0, 40, 30), lowerarm_l=(0, 0, -128), hand_l=(0, 0, 10))
    rest = dict(SIT, head=(0, 0, 6))
    TA.make("A_Earbuds", [(0.0, SIT, DOWN), (0.7, reach, DOWN), (1.0, grab, DOWN), (1.9, ear_r, DOWN), (2.5, both, DOWN), (3.1, both, DOWN), (3.9, rest, DOWN)], 3.9)
    return "ok"

# ---------------- input ----------------
def inputs():
    p = f"{R}/Core/IA_Interact"
    ia = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset("IA_Interact", f"{R}/Core", unreal.InputAction, unreal.InputAction_Factory())
    EAL.save_loaded_asset(ia, False)
    imc = EAL.load_asset("/Game/Input/IMC_Default")
    data = imc.get_editor_property("default_key_mappings"); maps = [m for m in data.get_editor_property("mappings") if m.get_editor_property("action") != ia]
    for key in ("E", "Gamepad_FaceButton_Left"):
        k = unreal.Key(); k.set_editor_property("key_name", key)
        m = unreal.EnhancedActionKeyMapping(); m.set_editor_property("action", ia); m.set_editor_property("key", k); maps.append(m)
    data.set_editor_property("mappings", maps); imc.set_editor_property("default_key_mappings", data); EAL.save_loaded_asset(imc, False)
    return "ok"

# ---------------- director blueprint ----------------
def director():
    if not EAL.does_asset_exist(DIR): BT.create(f"{R}/Core", "BP_IntroDirector", unreal.Actor.static_class())
    TG.ensure_vars(DIR, [("State", "int"), ("SeatYaw", "float")], objs=[("Chair", unreal.Actor.static_class()), ("Seat", unreal.Actor.static_class()),
                   ("SitDown", unreal.AnimSequence.static_class()), ("SitIdle", unreal.AnimSequence.static_class()), ("EarbudsAnim", unreal.AnimSequence.static_class())])
    g = lambda n: f"(Variables|Default|Get{n})"
    def tagged(tag, var, body): return f'(for {var} (Actor|GetAllActorswithTag :Tag "{tag}") {body})'
    def hint(tag, hidden): return tagged(tag, "h", f"(Rendering|SetActorHiddenInGame :self h :bNewHidden {hidden})")
    def cam(tag, blend): return tagged(tag, "c", f"(Game|Player|SetViewTargetwithBlend :self (Game|GetPlayerController 0) :NewViewTarget c :BlendTime {blend})")
    SIL = "(Utilities|Struct|MakeLinearColor :R 0.82 :G 0.88 :B 1.0 :A 1.0)"
    code = f"""
(event EventBeginPlay
  (Input|EnableInput :PlayerController (Game|GetPlayerController 0))
  (Variables|Default|SetState 0)
  {hint("HintSit", "true")}
  {hint("HintEarbuds", "true")})

(event EventTick (DeltaSeconds)
  (if (== {g('State')} 0)
    {hint("HintSit", "(> (Transformation|GetDistanceTo :self (Variables|Default|GetChair) :OtherActor (Game|GetPlayerCharacter 0)) 190.0)")}))

(event Custom|DoInteract
  (bind ch (Utilities|Casting|CastToCharacter :Object (Game|GetPlayerCharacter 0))
    (:then
      (if (and (== {g('State')} 0) (< (Transformation|GetDistanceTo :self (Variables|Default|GetChair) :OtherActor ch) 190.0))
        (Variables|Default|SetState 1)
        {hint("HintSit", "true")}
        (Pawn|Components|CharacterMovement|DisableMovement :self (Class|Character|GetCharacterMovement :self ch))
        (Collision|SetActorEnableCollision :self ch :bNewActorEnableCollision false)
        (Transformation|SetActorLocationAndRotation :self ch :NewLocation (Transformation|GetActorLocation :self (Variables|Default|GetSeat)) :NewRotation (Transformation|GetActorRotation :self (Variables|Default|GetSeat)) :bTeleport true)
        {cam("Cine_Seat", 1.2)}
        (Components|Animation|PlayAnimation :self (Class|Character|GetMesh :self ch) :NewAnimToPlay (Variables|Default|GetSitDown) :bLooping false)
        (Utilities|FlowControl|Delay 1.3)
        (Components|Animation|PlayAnimation :self (Class|Character|GetMesh :self ch) :NewAnimToPlay (Variables|Default|GetSitIdle) :bLooping true)
        {hint("HintEarbuds", "false")}
        (Variables|Default|SetState 2)
        (else
          (if (== {g('State')} 2)
            (Variables|Default|SetState 3)
            {hint("HintEarbuds", "true")}
            {cam("Cine_Ear", 1.0)}
            (Components|Animation|PlayAnimation :self (Class|Character|GetMesh :self ch) :NewAnimToPlay (Variables|Default|GetEarbudsAnim) :bLooping false)
            (Utilities|FlowControl|Delay 1.0)
            {tagged("Earbuds", "e", '(Transformation|AttachActorToComponent :self e :Parent (Class|Character|GetMesh :self ch) :SocketName "hand_r" :LocationRule "SnapToTarget" :RotationRule "KeepWorld" :ScaleRule "KeepWorld")')}
            (Utilities|FlowControl|Delay 1.3)
            {tagged("Earbuds", "e2", "(Rendering|SetActorHiddenInGame :self e2 :bNewHidden true)")}
            {tagged("IntroMusic", "m", "(bind am (Utilities|Casting|CastToAmbientSound :Object m) (:then (Components|Activation|Activate :self (Class|AmbientSound|GetAudioComponent :self am) :bReset true)) (:CastFailed))")}
            (Utilities|FlowControl|Delay 1.8)
            (Components|Animation|PlayAnimation :self (Class|Character|GetMesh :self ch) :NewAnimToPlay (Variables|Default|GetSitIdle) :bLooping true)
            {cam("Cine_1", 2.5)}
            (Utilities|FlowControl|Delay 3.5)
            {cam("Cine_2", 3.5)}
            (Utilities|FlowControl|Delay 4.0)
            {cam("Cine_3", 7.0)}
            (Utilities|FlowControl|Delay 5.5)
            (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager 0) :FromAlpha 0.0 :ToAlpha 1.0 :Duration 2.5 :Color {SIL} :bHoldWhenFinished true)
            (Utilities|FlowControl|Delay 2.6)
            (Game|OpenLevel(byName) :LevelName "M_FactoryHub")))))
    (:CastFailed)))
"""
    r = TG.run(DIR, code, events=["DoInteract"], binds=[("IA_Interact", [("Started", "DoInteract")])], clear=True)
    b = EAL.load_asset(DIR)
    for n in ("Chair", "Seat", "SitDown", "SitIdle", "EarbudsAnim"): BEL.set_blueprint_variable_instance_editable(b, n, True)
    BEL.compile_blueprint(b); EAL.save_loaded_asset(b, False)
    return str(r)[:400]

# ---------------- level ----------------
def level():
    L.load_level(f"{R}/Maps/M_RealRoom")
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() in ("Desk_Chair", "Seat_Point", "IntroDirector", "Cine_Seat", "Cine_Ear", "Hint_Sit", "Hint_Earbuds", "AnimProbe", "ProbeLight") or a.get_actor_label().startswith("AnimProbe"):
            E.destroy_actor(a)
    chair_mesh = EAL.load_asset("/Game/FreeFurniturePack/Meshes/SM_Modern_Office_chair")
    ch = E.spawn_actor_from_object(chair_mesh, V(-10, 118, 0), unreal.Rotator(roll=0, pitch=0, yaw=180))
    ch.set_actor_label("Desk_Chair"); ch.set_folder_path("Art/Room"); ch.tags = ["IntroChair"]
    o, e = ch.get_actor_bounds(False); l = ch.get_actor_location(); ch.set_actor_location(V(l.x, l.y, l.z - (o.z - e.z)), False, False)
    o, e = ch.get_actor_bounds(False)
    seat = E.spawn_actor_from_class(unreal.TargetPoint, V(o.x, o.y - 6, 96), unreal.Rotator(roll=0, pitch=0, yaw=90))
    seat.set_actor_label("Seat_Point"); seat.set_folder_path("Markers")
    def cine(name, loc, look, fov):
        c = E.spawn_actor_from_class(unreal.CineCameraActor, V(*loc), unreal.Rotator())
        d = V(look[0] - loc[0], look[1] - loc[1], look[2] - loc[2])
        c.set_actor_rotation(unreal.Rotator(roll=0, pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x))), False)
        cc = c.get_cine_camera_component(); cc.set_editor_property("current_focal_length", 35.0 * 0 + (36.0 / (2 * math.tan(math.radians(fov / 2)))))
        fs = cc.get_editor_property("focus_settings"); fs.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE); cc.set_editor_property("focus_settings", fs)
        c.set_actor_label(name); c.tags = [name]; c.set_folder_path("Cinematic"); return c
    sx, sy = o.x, o.y - 6
    cine("Cine_Seat", (sx + 95, sy - 140, 175), (sx, sy + 70, 105), 55)       # over the shoulder, desk in view
    cine("Cine_Ear", (sx - 70, sy + 35, 150), (sx - 8, sy + 2, 140), 40)      # side close-up: hand to ear
    c1 = find("Cine_1")
    if c1:
        c1.set_actor_location(V(sx - 42, sy + 22, 146), False, False)
        d = V(8, -20, -6); c1.set_actor_rotation(unreal.Rotator(roll=0, pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x))), False)
    def text(name, tag, msg, loc):
        t = E.spawn_actor_from_class(unreal.TextRenderActor, V(*loc), unreal.Rotator(roll=0, pitch=0, yaw=-90))
        tc = t.text_render; tc.set_text(unreal.Text(msg)); tc.set_world_size(5.0); tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
        tc.set_text_render_color(unreal.Color(r=230, g=235, b=255, a=255))
        t.set_actor_label(name); t.tags = [tag, "Intro"]; t.set_folder_path("UI"); return t
    text("Hint_Sit", "HintSit", "E  -  Sit down", (sx, sy - 10, 135))
    text("Hint_Earbuds", "HintEarbuds", "E  -  Put in your earbuds", (-35, 165, 100))
    for eb in E.get_all_level_actors():
        if unreal.Name("Earbuds") in eb.tags and isinstance(eb, unreal.StaticMeshActor):
            eb.root_component.set_mobility(unreal.ComponentMobility.MOVABLE); eb.set_actor_enable_collision(False)
    old = find("Hint_Headphones")
    if old: old.set_actor_hidden_in_game(True); old.tags = ["TUM_Built"]
    trg = find("Trigger_Headphones")
    if trg: trg.set_editor_property("bStartDisabled", True); trg.set_editor_property("Radius", 0.0)
    d = E.spawn_actor_from_class(EAL.load_asset(DIR).generated_class(), V(0, 0, 220), unreal.Rotator())
    d.set_actor_label("IntroDirector"); d.set_folder_path("Gameplay")
    d.set_editor_property("Chair", ch); d.set_editor_property("Seat", seat)
    for k, n in (("SitDown", "A_SitDown"), ("SitIdle", "A_SitIdle"), ("EarbudsAnim", "A_Earbuds")): d.set_editor_property(k, EAL.load_asset(f"{ANIMS}/{n}"))
    L.save_current_level()
    return {"chair": [round(o.x), round(o.y), round(o.z), round(e.x), round(e.y), round(e.z)]}

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    import sys
    if not EAL.does_asset_exist(f"{ANIMS}/A_Earbuds"): step("anims", anims)
    step("inputs", inputs); step("director", director)
    if "director" in res["ok"]: step("level", level)
    return res
