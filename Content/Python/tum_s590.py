# First person: camera at the eyes, own body hidden (shadow kept), sword held in view; cavalry knockdown = camera falls.
import unreal, importlib, traceback, inspect
import tum_graph as TG; importlib.reload(TG)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT, _BlueprintCache
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
CH = "/Game/TUM/Core/BP_TUMCharacter"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
SWORD_LOC = (58.0, 26.0, -26.0); SWORD_ROT = (12.0, -58.0, -10.0)   # roll, pitch, yaw

def camera():
    bp = EAL.load_asset(CH)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); F = unreal.SubobjectDataBlueprintFunctionLibrary
    out = []
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        d = F.get_data(h); o = F.get_object(d); n = str(F.get_variable_name(d))
        if n == "CameraBoom":
            o.set_editor_property("target_arm_length", 0.0); o.set_editor_property("relative_location", unreal.Vector(0, 0, 64))
            o.set_editor_property("use_pawn_control_rotation", True); o.set_editor_property("enable_camera_lag", False); o.set_editor_property("do_collision_test", False)
            o.set_editor_property("socket_offset", unreal.Vector(0, 0, 0)); o.set_editor_property("target_offset", unreal.Vector(0, 0, 0)); out.append(n)
        if n == "FollowCamera":
            o.set_editor_property("use_pawn_control_rotation", False); o.set_editor_property("field_of_view", 90.0)
            o.set_editor_property("relative_location", unreal.Vector(0, 0, 0)); o.set_editor_property("relative_rotation", unreal.Rotator()); out.append(n)
        if n == "Mesh":
            o.set_editor_property("owner_no_see", True); o.set_editor_property("cast_hidden_shadow", True); out.append(n)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("use_controller_rotation_yaw", True)
    cm = cdo.get_editor_property("character_movement"); cm.set_editor_property("orient_rotation_to_movement", False)
    BEL.compile_blueprint(bp); EAL.save_loaded_asset(bp, False)
    return out

def sword():
    b = EAL.load_asset(CH); _BlueprintCache.invalidate(b); g = unreal.BlueprintEditorLibrary.find_event_graph(b)
    for n in list(BT.find_nodes(g)):
        t = BT._get_node_info(n).type_id
        if t in ("AddEvent|EventBeginPlay", "Transformation|AttachComponentToComponent", "Transformation|SetRelativeRotation", "Transformation|SetRelativeLocation"): BT.delete_node(n)
    _BlueprintCache.invalidate(b)
    code = f"""
(event EventBeginPlay
  (Transformation|AttachComponentToComponent :self (Variables|Default|GetSword) :Parent (Variables|Camera|GetFollowCamera) :SocketName "None" :LocationRule "SnapToTarget" :RotationRule "SnapToTarget" :ScaleRule "KeepWorld" :bWeldSimulatedBodies false)
  (Transformation|SetRelativeRotation :self (Variables|Default|GetSword) :NewRotation (Math|Rotator|MakeRotator :Roll {SWORD_ROT[0]} :Pitch {SWORD_ROT[1]} :Yaw {SWORD_ROT[2]}))
  (Transformation|SetRelativeLocation :self (Variables|Default|GetSword) :NewLocation (Math|Vector|MakeVector {SWORD_LOC[0]} {SWORD_LOC[1]} {SWORD_LOC[2]})))
"""
    return str(TG.run(CH, code, clear=False))[:200]

def cavalry():
    import tum_s580 as C; importlib.reload(C)
    src = inspect.getsource(C.cavalry_bp)
    old_start = src.index("(event Custom|KnockDown")
    old_end = src.index("(event EventTick (DeltaSeconds)")
    cam = "(Class|BPThirdPersonCharacter|GetFollowCamera :self ch)"
    down = "\n".join(f"      (Transformation|SetRelativeLocationAndRotation :self {cam} :NewLocation (Math|Vector|MakeVector 0.0 0.0 {-22.0 * k}) :NewRotation (Math|Rotator|MakeRotator :Roll {13.0 * k} :Pitch {7.0 * k} :Yaw 0.0))\n      (Utilities|FlowControl|Delay 0.03)" for k in range(1, 7))
    up = "\n".join(f"      (Transformation|SetRelativeLocationAndRotation :self {cam} :NewLocation (Math|Vector|MakeVector 0.0 0.0 {-22.0 * k}) :NewRotation (Math|Rotator|MakeRotator :Roll {13.0 * k} :Pitch {7.0 * k} :Yaw 0.0))\n      (Utilities|FlowControl|Delay 0.06)" for k in range(5, -1, -1))
    new = f"""(event Custom|KnockDown
  (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object {{PL}})
    (:then
      (Input|DisableInput :self ch :PlayerController (Game|GetPlayerController 0))
{down}
      (Utilities|FlowControl|Delay 1.2)
{up}
      (Input|EnableInput :self ch :PlayerController (Game|GetPlayerController 0)))
    (:CastFailed)))

"""
    src = src[:old_start] + new + src[old_end:]
    ns = dict(C.__dict__); exec(src, ns); return ns["cavalry_bp"]()

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("camera", camera); step("sword", sword); step("cavalry", cavalry)
    return res
