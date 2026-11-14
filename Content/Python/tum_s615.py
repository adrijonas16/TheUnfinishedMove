# HUD only (left objective banner, hidden when paused). Sword swing / stress / heartbeat moved out of the HUD graph:
# the bigger graph made the editor run out of memory while building it.
import unreal, importlib, inspect
import tum_s610 as X; importlib.reload(X)
import tum_graph as TG
SW_START = "      (bind sword (Class|BPTUMCharacter|GetSword :self ch))"
SW_END = "        (Pawn|AddControllerYawInput :self ch :Val (* (* (Math|Trig|Cos(Radians) (* now 6.3)) 0.04) stress)))\n"
VG_START = "    (if (< hp2 70.0)\n"
VG_END = "{g('H')} 0.07)\")})\n"
def hud():
    src = inspect.getsource(X.hud_bp)
    a = src.index(SW_START); b = src.index(SW_END) + len(SW_END); src = src[:a] + src[b:]
    a = src.index(VG_START); b = src.index(VG_END, a) + len(VG_END); src = src[:a] + src[b:]
    unreal.SystemLibrary.collect_garbage()
    ns = dict(X.__dict__); exec(src, ns); return ns["hud_bp"]()
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    res = {}
    import traceback
    try: res["hud"] = str(hud())[:400]
    except Exception: res["err"] = traceback.format_exc()[-1500:]
    return res
