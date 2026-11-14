# Same HUD build as s615, but frees editor memory (garbage collection) every few node operations.
# Each node/wire triggers a Blueprint skeleton rebuild whose garbage is normally freed between frames;
# a long script runs in one frame, so it piled up until the editor ran out of memory.
import unreal, importlib, traceback, gc
import tum_s615 as H; importlib.reload(H)
import tum_graph as TG
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
from editor_toolset.toolsets import blueprint_dsl
N = {"ops": 0, "gc": 0}
def _tick():
    N["ops"] += 1
    if N["ops"] % 30 == 0:
        gc.collect(); unreal.SystemLibrary.collect_garbage(); N["gc"] += 1
_OC, _OK, _OD = BT.create_node, BT.connect_pins, BT.delete_node
def _create(graph, type_id, pos, declaring_class=None):
    _tick(); return _OC(graph, type_id, pos, declaring_class)
def _connect(a, b):
    _tick(); return _OK(a, b)
def _delete(n):
    _tick(); return _OD(n)
def _set(p, v):
    return BT.set_pin_value(p, v)
_ft = {}
def _find_types(graph, f, *a):
    k = (f, tuple(a[0]) if a and isinstance(a[0], (list, tuple)) else None)
    if k not in _ft: _ft[k] = BT.find_node_types(graph, f, *a)
    return _ft[k]
def write(graph, code):
    blueprint_dsl.Transpiler(graph, _create, _connect, BT._get_node_info, _set, lambda g: BT.find_nodes(g),
                             delete_node_fn=_delete,
                             find_node_types_fn=lambda f: _find_types(graph, f)).transpile(code)
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    old = TG.write; TG.write = write; BT.delete_node = _delete
    res = {}
    try: res["hud"] = str(H.hud())[:400]
    except Exception: res["err"] = traceback.format_exc()[-1500:]
    finally: TG.write = old; BT.delete_node = _OD
    res["ops"] = dict(N); return res
