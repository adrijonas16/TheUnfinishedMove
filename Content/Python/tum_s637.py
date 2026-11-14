# Root cause of horses (and knights) ignoring walls: a trace node used inline in a condition got its *OutHit* output wired
# instead of its true/false result (the log said "Could not connect pin OutHit to A"), so every wall check read as "no wall".
# Fix: hoist each trace into its own (bind (hit result) ...) right before the statement that uses it, then use the result.
import unreal, importlib, traceback
import tum_s626 as K626; importlib.reload(K626)
import tum_s632 as C632; importlib.reload(C632)
from editor_toolset.toolsets import blueprint_dsl
TRUE_ORIG = blueprint_dsl.Transpiler.transpile
res = {"hoisted": {}}
def expr_at(s, i):
    d = 0
    for j in range(i, len(s)):
        d += (s[j] == "(") - (s[j] == ")")
        if d == 0: return s[i:j + 1]
    raise RuntimeError("unbalanced")
def hoist(code):
    n = 0; idx = 0
    while True:
        cands = [k for k in (code.find("(Collision|LineTraceByChannel", idx), code.find("(Collision|BoxTraceByChannel", idx)) if k >= 0]
        if not cands: break
        i = min(cands); ls = code.rfind("\n", 0, i) + 1; line = code[ls:i]
        if line.lstrip().startswith("(bind (oh"): idx = i + 1; continue
        e = expr_at(code, i); ind = line[:len(line) - len(line.lstrip())]
        code = code[:ls] + f"{ind}(bind (oh{n} th{n}) {e})\n" + code[ls:i] + f"th{n}" + code[i + len(e):]
        n += 1; idx = ls
    return code, n
def wrapped(self, code):
    try: path = self.graph.get_outer().get_path_name()
    except Exception: path = ""
    if "BP_Knight" in path or "BP_Cavalry" in path:
        code, n = hoist(code); res["hoisted"][path.split(".")[-1]] = n
    return TRUE_ORIG(self, code)
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    K626.K._orig = wrapped                      # knights: s617 strike transform runs first, then this
    try: res["knight"] = K626.run()
    except Exception: res["knight_err"] = traceback.format_exc()[-1500:]
    blueprint_dsl.Transpiler.transpile = wrapped
    try: res["cavalry"] = C632.run()
    except Exception: res["cav_err"] = traceback.format_exc()[-1500:]
    finally: blueprint_dsl.Transpiler.transpile = TRUE_ORIG
    return res
