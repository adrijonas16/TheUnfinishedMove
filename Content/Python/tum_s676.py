# War: rocks and arrows land both near you and at random around the field (not in one cluster).
import unreal, importlib, inspect, traceback
import tum_s510 as B; importlib.reload(B)
import tum_s666 as Q
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
SPREAD = "(* (Math|Random|RandomFloatinRange :Min -1.0 :Max 1.0) (select (Math|Random|RandomBool) 220.0 1900.0))"
def catapult():
    src = inspect.getsource(B.catapult_bp); old = "(Math|Random|RandomFloatinRange :Min -220.0 :Max 220.0)"
    assert src.count(old) == 2
    src = src.replace(old, SPREAD)
    ns = dict(B.__dict__); exec(src, ns); return Q.patched(lambda: str(ns["catapult_bp"]())[:300])
def archers():
    src = inspect.getsource(B.archers_bp); old = "(Math|Random|RandomFloatinRange :Min -360.0 :Max 360.0)"
    assert src.count(old) == 2
    src = src.replace(old, "(Math|Random|RandomFloatinRange :Min {-360.0 if k < 2 else -2400.0} :Max {360.0 if k < 2 else 2400.0})")
    ns = dict(B.__dict__); exec(src, ns); return Q.patched(lambda: str(ns["archers_bp"]())[:300])
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_WarField")
    step("catapult", catapult); step("archers", archers)
    L.save_current_level(); return res
