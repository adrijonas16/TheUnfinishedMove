# War knights: realistic sword reach. They walk right up to you (about 1 m), swing, and the blow lands 0.35 s later
# only if you are still within ~1.5 m. Push-back is softer. Distance is measured flat (ignores height).
import unreal, importlib, traceback, gc
import tum_s566 as K566; importlib.reload(K566)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT, _BlueprintCache
from editor_toolset.toolsets import blueprint_dsl
res = {}

def expr_at(s, i):
    d = 0
    for j in range(i, len(s)):
        d += (s[j] == "(") - (s[j] == ")")
        if d == 0: return s[i:j + 1]
    raise RuntimeError("unbalanced at %d" % i)

def transform(code):
    i = code.index("(bind d (Transformation|GetDistanceTo")
    e = expr_at(code, i)
    dh = "\n  (bind dh (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pp) (.x me)) (- (.y pp) (.y me)) 0.0)))"
    code = code[:i + len(e)] + dh + code[i + len(e):]
    for a, b in (("(> d 190.0)", "(> dh 100.0)"), ("(if (< d 190.0)", "(if (< dh 125.0)")):
        if a not in code: raise RuntimeError("missing " + a)
        code = code.replace(a, b)
    t = code.index("(event EventTick")
    i = code.index("(bind ch (Utilities|Casting|CastToBP_TUMCharacter", t)
    hit = expr_at(code, i)
    code = code[:i] + "(CallFunction|Strike)" + code[i + len(hit):]
    hit = hit.replace("(.x me)) 3.0)", "(.x me)) 1.5)").replace("(.y me)) 3.0)", "(.y me)) 1.5)").replace(" 250.0)", " 150.0)")
    code += f"""
(event Custom|Strike
  (Utilities|FlowControl|Delay 0.35)
  (bind me (Transformation|GetActorLocation))
  (bind pp (Transformation|GetActorLocation :self (Game|GetPlayerCharacter 0)))
  (if (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pp) (.x me)) (- (.y pp) (.y me)) 0.0)) 150.0)
    {hit}))
"""
    return code

_orig = blueprint_dsl.Transpiler.transpile
def _transpile(self, code):
    try: path = self.graph.get_outer().get_path_name()
    except Exception: path = ""
    if "BP_Knight" in path and "Custom|Strike" not in code:
        bp = self.graph.get_outer()
        BT.add_event(bp, "Strike"); _BlueprintCache.invalidate(bp)
        code = transform(code); res["transformed"] = True
    return _orig(self, code)

N = {"ops": 0}
_OC, _OK = BT.create_node, BT.connect_pins
def _c(*a):
    N["ops"] += 1
    if N["ops"] % 40 == 0: gc.collect(); unreal.SystemLibrary.collect_garbage()
    return _OC(*a)
def _k(*a):
    N["ops"] += 1
    if N["ops"] % 40 == 0: gc.collect(); unreal.SystemLibrary.collect_garbage()
    return _OK(*a)

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    blueprint_dsl.Transpiler.transpile = _transpile; BT.create_node = _c; BT.connect_pins = _k
    try: res["knight"] = str(K566.knight())[:400]
    except Exception: res["err"] = traceback.format_exc()[-1800:]
    finally: blueprint_dsl.Transpiler.transpile = _orig; BT.create_node = _OC; BT.connect_pins = _OK
    res["ops"] = N["ops"]; return res
