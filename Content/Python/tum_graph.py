# Blueprint graph writer for The Unfinished Move.
# Adapted from editor tooling written before the jam for an unrelated project (declared in PRE_JAM_DECLARATION.md);
# it wraps Epic's editor_toolset Blueprint DSL (AllToolsets plugin). No gameplay from that project is reused.
import unreal, re, json, traceback
from editor_toolset.toolsets.blueprint import BlueprintTools as BT, _BlueprintCache
from editor_toolset.toolsets import blueprint_dsl
EAL = unreal.EditorAssetLibrary
def _create(graph, type_id, pos, declaring_class=None): return BT.create_node(graph, type_id, pos, declaring_class)
def write(graph, code):
    blueprint_dsl.Transpiler(graph, _create, BT.connect_pins, BT._get_node_info, BT.set_pin_value, lambda g: BT.find_nodes(g),
                             delete_node_fn=BT.delete_node, find_node_types_fn=lambda f: BT.find_node_types(graph, f)).transpile(code)
def check_ids(graph, code):
    ids = set(re.findall(r'\(([A-Za-z][\w]*\|[^\s()]+(?:\([^\s()]*\))?)', code)); miss = []
    for t in sorted(ids):
        if t.startswith("AddEvent|"): continue
        try:
            if not any(f.lower() == t.lower() for f in BT.find_node_types(graph, t)): miss.append(t)
        except Exception: miss.append(t + " ERR")
    return miss
def balance(code):
    d = 0
    for ch in code:
        d += (ch == "(") - (ch == ")")
    return d
def run(bp_path, code, events=(), binds=()):
    """events: custom events to add first. binds: [(IA name, [(trigger pin, custom event)])] wired after the graph is written."""
    O = {"ok": [], "missing": [], "balance": balance(code)}
    if O["balance"]: raise RuntimeError("unbalanced parens: %d" % O["balance"])
    bp = EAL.load_asset(bp_path); _BlueprintCache.invalidate(bp)
    for ev in events: BT.add_event(bp, ev)
    _BlueprintCache.invalidate(bp); graph = unreal.BlueprintEditorLibrary.find_event_graph(bp)
    miss = check_ids(graph, code); O["missing"] = miss
    if miss: raise RuntimeError("missing nodes: %s" % miss)
    write(graph, code); BT.compile_blueprint(bp); EAL.save_loaded_asset(bp, False); O["ok"].append("graph")
    _BlueprintCache.invalidate(bp); g = unreal.BlueprintEditorLibrary.find_event_graph(bp); y = 6000
    for ia, bl in binds:
        src = [f for f in BT.find_node_types(g, ia) if f.startswith("Input|EnhancedActionEvents|")][0]
        n = BT.create_node(g, src, unreal.IntPoint(-400, y))
        for pin, ev in bl:
            ct = [f for f in BT.find_node_types(g, ev) if f == f"CallFunction|{ev}"][0]
            c = BT.create_node(g, ct, unreal.IntPoint(0, y)); y += 200
            outs = [p for p in BT._get_node_info(n).output_pins if p.name == pin]
            ex = [p for p in BT._get_node_info(c).input_pins if p.name == "execute"][0]
            BT.connect_pins(outs[0].pin_id, ex.pin_id)
        y += 200
    BT.compile_blueprint(bp); EAL.save_loaded_asset(bp, False); O["ok"].append("inputs")
    return O
