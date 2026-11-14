# War: (1) cavalry rewritten from scratch - a horse is never seen standing. Each one waits parked out of the map, picks a
#          random start 24-33 m from you, checks the whole lane with a box sweep, then gallops through and past you and
#          leaves; repeats forever.  (2) the goal needs a key press (Enhanced Input IA_Interact).  (3) thick fog.
import unreal, importlib, traceback, gc
import tum_s580 as C; importlib.reload(C)
import tum_s612 as T612
import tum_graph as TG
from editor_toolset.toolsets.blueprint import BlueprintTools as BT, _BlueprintCache
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"; CH = f"{R}/Core/BP_TUMCharacter"; PL = C.PL
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
N = {"ops": 0}
_OC, _OK = BT.create_node, BT.connect_pins
def _gc():
    N["ops"] += 1
    if N["ops"] % 40 == 0: gc.collect(); unreal.SystemLibrary.collect_garbage()
def _c(*a): _gc(); return _OC(*a)
def _k(*a): _gc(); return _OK(*a)
def patched(fn):
    BT.create_node = _c; BT.connect_pins = _k; T612.TG.run = T612._run2
    try: return fn()
    finally: T612.TG.run = T612._orig_run; BT.create_node = _OC; BT.connect_pins = _OK

g = lambda n: f"(Variables|Default|Get{n})"
def s(n, v): return f"(Variables|Default|Set{n} {v})"
def rnd(a, b): return f"(Math|Random|RandomFloatinRange :Min {a} :Max {b})"
def vec(x, y, z): return f"(Math|Vector|MakeVector {x} {y} {z})"
def clamp(v, a, b): return f"(Math|Float|Clamp(Float) {v} {a} {b})"
YAW = f"(Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (Math|Trig|Atan2(Degrees) {g('DY')} {g('DX')}))"
def box(start, end): return f"(Collision|BoxTraceByChannel :Start {start} :End {end} :HalfSize {vec(60.0, 70.0, 80.0)} :Orientation {YAW})"
PARK = f"(Transformation|SetActorLocation :NewLocation {vec(0.0, 0.0, -6000.0)} :bTeleport true)"

def cavalry_code():
    cam = "(Class|BPThirdPersonCharacter|GetFollowCamera :self ch)"
    def camstep(k, d): return (f"      (Transformation|SetRelativeLocationAndRotation :self {cam} :NewLocation {vec(0.0, 0.0, -20.0 * k)} "
                               f":NewRotation (Math|Rotator|MakeRotator :Roll {12.0 * k} :Pitch {6.0 * k} :Yaw 0.0))\n      (Utilities|FlowControl|Delay {d})")
    down = "\n".join(camstep(k, 0.03) for k in range(1, 7)); up = "\n".join(camstep(k, 0.035) for k in range(5, -1, -1))
    gz130 = f"(+ {g('GZ')} 130.0)"
    lane = box(vec(g('SX'), g('SY'), gz130), vec(f"(+ {g('SX')} (* {g('DX')} {g('Len')}))", f"(+ {g('SY')} (* {g('DY')} {g('Len')}))", gz130))
    ahead = box(vec(f"(+ (.x me) (* {g('DX')} 20.0))", f"(+ (.y me) (* {g('DY')} 20.0))", gz130), vec(f"(+ (.x me) (* {g('DX')} 260.0))", f"(+ (.y me) (* {g('DY')} 260.0))", gz130))
    return f"""
(event EventBeginPlay
  (bind l0 (Transformation|GetActorLocation))
  {s('GZ', '(.z l0)')}
  {s('State', 0)}
  {s('Wait', rnd(1.0, 7.0))}
  {C.play('Horse', g('Gallop'))}
  {PARK})

(event Custom|KnockDown
  (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object {PL})
    (:then
{down}
      (Utilities|FlowControl|Delay 0.25)
{up})
    (:CastFailed)))

(event EventTick (DeltaSeconds)
  (bind pl (Transformation|GetActorLocation :self {PL}))
  (if (== {g('State')} 0)
    {s('Wait', f"(- {g('Wait')} DeltaSeconds)")}
    (if (< {g('Wait')} 0.0)
      {s('Ang', rnd(0.0, 6.283))}
      {s('Rad', rnd(2400.0, 3300.0))}
      {s('SX', clamp(f"(+ (.x pl) (* (Math|Trig|Cos(Radians) {g('Ang')}) {g('Rad')}))", -700.0, 9900.0))}
      {s('SY', clamp(f"(+ (.y pl) (* (Math|Trig|Sin(Radians) {g('Ang')}) {g('Rad')}))", -4300.0, 4300.0))}
      {s('TX', f"(+ (.x pl) {rnd(-280.0, 280.0)})")}
      {s('TY', f"(+ (.y pl) {rnd(-280.0, 280.0)})")}
      (bind ddx (- {g('TX')} {g('SX')}))
      (bind ddy (- {g('TY')} {g('SY')}))
      (bind dl (Math|Vector|VectorLength {vec('ddx', 'ddy', 0.0)}))
      (if (> dl 1700.0)
        {s('DX', '(/ ddx dl)')}
        {s('DY', '(/ ddy dl)')}
        {s('Len', '(+ dl 1500.0)')}
        (bind (oh1 blocked) {lane})
        (if (not blocked)
          {s('State', 1)}
          {s('Run', 0.0)}
          {s('Hit', 'false')}
          (Transformation|SetActorLocationAndRotation :NewLocation {vec(g('SX'), g('SY'), g('GZ'))} :NewRotation {YAW} :bTeleport true)
          (Audio|PlaySoundatLocation :Sound {g('Hoof')} :Location {vec(g('SX'), g('SY'), g('GZ'))} :VolumeMultiplier 1.2 :PitchMultiplier 0.7)))))
  (if (== {g('State')} 1)
    (bind me (Transformation|GetActorLocation))
    (bind step (* (* {g('Speed')} DeltaSeconds) (+ 0.45 (* 0.55 {clamp(f"(/ {g('Run')} 700.0)", 0.0, 1.0)}))))
    {s('Run', f"(+ {g('Run')} step)")}
    (Transformation|SetActorLocation :NewLocation {vec(f"(+ (.x me) (* {g('DX')} step))", f"(+ (.y me) (* {g('DY')} step))", "(.z me)")} :bTeleport true)
    (bind dp (Math|Vector|VectorLength {vec("(- (.x pl) (.x me))", "(- (.y pl) (.y me))", 0.0)}))
    (bind (oh2 wall) {ahead})
    (if (or wall (> {g('Run')} {g('Len')}))
      {s('State', 0)}
      {s('Wait', rnd(0.8, 3.0))}
      {PARK})
    (if (and (and (< dp 200.0) (not {g('Hit')})) (== {g('State')} 1))
      {s('Hit', 'true')}
      (Audio|PlaySoundatLocation :Sound {g('Thud')} :Location pl :VolumeMultiplier 1.3 :PitchMultiplier 0.8)
      (CallFunction|KnockDown)
      (bind ch2 (Utilities|Casting|CastToBP_TUMCharacter :Object {PL})
        (:then
          (Character|LaunchCharacter :self ch2 :LaunchVelocity {vec(f"(* {g('DX')} 900.0)", f"(* {g('DY')} 900.0)", 420.0)} :bXYOverride true :bZOverride true)
          (Class|BPTUMCharacter|SetHealth :self ch2 :Health (- (Class|BPTUMCharacter|GetHealth :self ch2) 28.0))
          (Class|BPTUMCharacter|SetLastHit :self ch2 :LastHit (Utilities|Time|GetGameTimeinSeconds)))
        (:CastFailed)))))
"""
def cavalry():
    p = f"{WB}/BP_Cavalry"
    TG.ensure_vars(p, [(n, "float") for n in ("Ang", "Rad", "SX", "SY", "Len", "GZ")])
    return patched(lambda: str(TG.run(p, cavalry_code(), events=["KnockDown"], clear=True))[:300])

# ---------------- goal needs a key ----------------
def interact_input():
    imc = EAL.load_asset("/Game/Input/IMC_Default"); data = imc.get_editor_property("default_key_mappings")
    maps = list(data.get_editor_property("mappings"))
    p = f"{R}/Core/IA_Interact"
    act = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset("IA_Interact", f"{R}/Core", unreal.InputAction, unreal.InputAction_Factory())
    EAL.save_loaded_asset(act)
    used = {str(m.get_editor_property("key").get_editor_property("key_name")) for m in maps if m.get_editor_property("action") != act}
    key = next(k for k in ("E", "F", "Enter") if k not in used)
    pad = next((k for k in ("Gamepad_FaceButton_Left", "Gamepad_FaceButton_Top") if k not in used), None)
    maps = [m for m in maps if m.get_editor_property("action") != act]
    for kn in [key] + ([pad] if pad else []):
        k = unreal.Key(); k.set_editor_property("key_name", kn)
        m = unreal.EnhancedActionKeyMapping(); m.set_editor_property("action", act); m.set_editor_property("key", k); maps.append(m)
    data.set_editor_property("mappings", maps); imc.set_editor_property("default_key_mappings", data); EAL.save_loaded_asset(imc, False)
    return key
def interact_event():
    bp = EAL.load_asset(CH); _BlueprintCache.invalidate(bp); gr = BEL.find_event_graph(bp)
    if any("DoInteract" in BT._get_node_info(n).type_id for n in BT.find_nodes(gr)): return "exists"
    code = """
(event Custom|DoInteract
  (for t (Actor|GetAllActorswithTag :Tag "UseGoal")
    (if (< (Transformation|GetDistanceTo :OtherActor t) 300.0)
      (Actor|Tick|SetActorTickEnabled :self t :bEnabled true))))
"""
    return patched(lambda: str(TG.run(CH, code, events=["DoInteract"], binds=[("IA_Interact", [("Started", "DoInteract")])], clear=False))[:300])
def goal_level(key):
    out = {}
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() == "Goal_Prompt": E.destroy_actor(a)
    for a in E.get_all_level_actors():
        if a.get_class().get_name() == "BP_Trigger_C":
            a.set_editor_property("bStartDisabled", True); a.set_editor_property("Radius", 320.0); a.tags = [unreal.Name("UseGoal")]
            l = a.get_actor_location(); out["trigger"] = [a.get_actor_label(), round(l.x), round(l.y)]
            t = E.spawn_actor_from_class(unreal.TextRenderActor, V(l.x - 30, l.y, l.z + 150), unreal.Rotator(roll=0, pitch=0, yaw=180))
            tc = t.text_render; tc.set_text(unreal.Text(f"[{key}]  TAKE THE SEAL")); tc.set_world_size(22.0); tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
            tc.set_text_render_color(unreal.Color(r=255, g=214, b=150, a=255)); t.set_actor_label("Goal_Prompt"); t.set_folder_path("Gameplay/Goal")
    return out

def fog():
    out = {}
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.ExponentialHeightFog):
            fc = a.get_editor_property("component"); l = a.get_actor_location()
            out["before"] = {"z": l.z, "hidden": a.is_hidden_ed(), "visible": fc.get_editor_property("visible"), "density": fc.get_editor_property("fog_density"),
                             "cutoff": fc.get_editor_property("fog_cutoff_distance"), "start": fc.get_editor_property("start_distance")}
            a.set_actor_location(V(l.x, l.y, 0.0), False, False)
            fc.set_editor_property("visible", True); fc.set_editor_property("fog_density", 0.6); fc.set_editor_property("fog_height_falloff", 0.6)
            fc.set_editor_property("start_distance", 0.0); fc.set_editor_property("fog_cutoff_distance", 0.0); fc.set_editor_property("fog_max_opacity", 1.0)
            fc.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.09, 0.10, 0.125, 1.0))
            try: fc.set_editor_property("directional_inscattering_luminance", unreal.LinearColor(0.0, 0.0, 0.0, 1.0))
            except Exception: pass
            out["after"] = "z0 density 0.6 falloff 0.6"
    return out

def probe():
    a = E.spawn_actor_from_class(EAL.load_asset(CH).generated_class(), V(0, 0, -20000))
    try: return [c.get_editor_property("target_arm_length") for c in a.get_components_by_class(unreal.SpringArmComponent)]
    finally: E.destroy_actor(a)

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("cavalry", cavalry)
    step("key", interact_input)
    if "key" in res["ok"]: step("interact_event", interact_event)
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    if "interact_event" in res["ok"]: step("goal_level", lambda: goal_level(res["key"]))
    step("fog", fog)
    L.save_current_level()
    res["arm_after"] = probe(); res["ops"] = N["ops"]
    return res
