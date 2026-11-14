# Horses (v2): box sweep ahead (catches thin planks/stakes), gallop accelerates from a standstill.
# Horses: wall check starts at the horse's chest (not 1.5 m ahead, which let a horse parked at a wall pass through it on the next charge),
# line of sight goes all the way to you, and a horse only hurts you while it is actually charging.
import unreal, importlib, inspect, gc, traceback
import tum_s612 as T; importlib.reload(T)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
BOX = "(Collision|BoxTraceByChannel :Start (Math|Vector|MakeVector (+ (.x me) (* {{g('DX')}} 20.0)) (+ (.y me) (* {{g('DY')}} 20.0)) (+ (.z me) 120.0)) :End (Math|Vector|MakeVector (+ (.x me) (* {{g('DX')}} 620.0)) (+ (.y me) (* {{g('DY')}} 620.0)) (+ (.z me) 120.0)) :HalfSize (Math|Vector|MakeVector 70.0 70.0 95.0) :Orientation (Transformation|GetActorRotation))"
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
    reps = [("(or {{_tr(60.0)}} {{_tr(170.0)}})", BOX),
            ("(* {{g('DX')}} 150.0)) (+ (.y me) (* {{g('DY')}} 150.0))", "(* {{g('DX')}} 20.0)) (+ (.y me) (* {{g('DY')}} 20.0))"),
            ("(* (/ dpx (+ dp 1.0)) 160.0)) (- (.y pl) (* (/ dpy (+ dp 1.0)) 160.0))", "(* (/ dpx (+ dp 1.0)) 60.0)) (- (.y pl) (* (/ dpy (+ dp 1.0)) 60.0))"),
            ("    ns = dict(C.__dict__); exec(src, ns)",
             "    src = src.replace(\"(if (and (< dp 210.0) (not {g('Hit')}))\", \"(if (and (and (< dp 210.0) (not {g('Hit')})) (== {g('State')} 1))\").replace(\"(bind step (* {g('Speed')} DeltaSeconds))\", \"(bind step (* (* {g('Speed')} DeltaSeconds) (+ 0.3 (* 0.7 (Math|Float|Clamp(Float) (/ {g('Run')} 800.0) 0.0 1.0)))))\")\n    ns = dict(C.__dict__); exec(src, ns)")]
    for a, b in reps:
        assert src.count(a) == 1, a[:50]
        src = src.replace(a, b)
    ns = dict(T.__dict__); exec(src, ns)
    BT.create_node = _c; BT.connect_pins = _k; T.TG.run = T._run2
    try: r = ns["cavalry"]()
    except Exception: r = traceback.format_exc()[-1500:]
    finally: BT.create_node = _OC; BT.connect_pins = _OK; T.TG.run = T._orig_run
    return {"cavalry": str(r)[:400], "ops": N["ops"]}
