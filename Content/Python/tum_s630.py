# Horses: wall check starts at the horse's chest (not 1.5 m ahead, which let a horse parked at a wall pass through it on the next charge),
# line of sight goes all the way to you, and a horse only hurts you while it is actually charging.
import unreal, importlib, inspect, gc, traceback
import tum_s612 as T; importlib.reload(T)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
N = {"ops": 0}
_OC, _OK = BT.create_node, BT.connect_pins
def _gc():
    N["ops"] += 1
    if N["ops"] % 40 == 0: gc.collect(); unreal.SystemLibrary.collect_garbage()
def _c(*a): _gc(); return _OC(*a)
def _k(*a): _gc(); return _OK(*a)
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    src = inspect.getsource(T.cavalry)
    reps = [("(* {{g('DX')}} 150.0)) (+ (.y me) (* {{g('DY')}} 150.0))", "(* {{g('DX')}} 20.0)) (+ (.y me) (* {{g('DY')}} 20.0))"),
            ("(* (/ dpx (+ dp 1.0)) 160.0)) (- (.y pl) (* (/ dpy (+ dp 1.0)) 160.0))", "(* (/ dpx (+ dp 1.0)) 60.0)) (- (.y pl) (* (/ dpy (+ dp 1.0)) 60.0))"),
            ("    ns = dict(C.__dict__); exec(src, ns)",
             "    src = src.replace(\"(if (and (< dp 210.0) (not {g('Hit')}))\", \"(if (and (and (< dp 210.0) (not {g('Hit')})) (== {g('State')} 1))\")\n    ns = dict(C.__dict__); exec(src, ns)")]
    for a, b in reps:
        assert src.count(a) == 1, a[:50]
        src = src.replace(a, b)
    ns = dict(T.__dict__); exec(src, ns)
    BT.create_node = _c; BT.connect_pins = _k
    try: r = ns["cavalry"]()
    except Exception: r = traceback.format_exc()[-1500:]
    finally: BT.create_node = _OC; BT.connect_pins = _OK
    return {"cavalry": str(r)[:400], "ops": N["ops"]}
