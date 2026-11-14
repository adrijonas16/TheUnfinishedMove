# Horses: fewer and spread out. 4 horses (was 7), 6-14 s between charges each, and a lane that was just used is not
# reused by any horse for 25 s (the lane marker remembers when it was last used), so they come from different places.
import unreal, importlib, traceback
import tum_s671 as A; importlib.reload(A)
import tum_graph as TG
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; Q = A.Q; g = Q.g
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def code():
    c = A.cavalry_code()
    reps = [("(if (< (+ dist (Math|Random|RandomFloatinRange :Min 0.0 :Max 900.0)) (Variables|Default|GetBest))",
             "(if (and (> (- (Utilities|Time|GetGameTimeinSeconds) (.z ll)) 25.0) (< (+ dist (Math|Random|RandomFloatinRange :Min 0.0 :Max 1500.0)) (Variables|Default|GetBest)))"),
            ("          (Variables|Default|SetBest dist)\n", "          (Variables|Default|SetBest dist)\n          (Variables|Default|SetBestLane ln)\n"),
            ("        (Variables|Default|SetState 1)\n", "        (Variables|Default|SetState 1)\n        (bind bl (Transformation|GetActorLocation :self (Variables|Default|GetBestLane)))\n        (Transformation|SetActorLocation :self (Variables|Default|GetBestLane) :NewLocation (Math|Vector|MakeVector (.x bl) (.y bl) (Utilities|Time|GetGameTimeinSeconds)) :bTeleport true)\n"),
            ("(Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 0.8 :Max 3.0))", "(Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 6.0 :Max 14.0))"),
            ("(Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 1.0 :Max 7.0))", "(Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 3.0 :Max 14.0))"),
            ("(Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 0.6 :Max 1.5))", "(Variables|Default|SetWait (Math|Random|RandomFloatinRange :Min 1.0 :Max 2.5))")]
    for a, b in reps:
        assert c.count(a) == 1, a[:70]
        c = c.replace(a, b)
    assert TG.balance(c) == 0
    return c
def cavalry():
    p = f"{A.WB}/BP_Cavalry"
    TG.ensure_vars(p, [], objs=[("BestLane", unreal.Actor.static_class())])
    c = code()
    return Q.patched(lambda: str(TG.run(p, c, events=["KnockDown"], clear=True))[:300])
def level():
    out = {"lanes": 0, "removed": 0}
    cav = sorted([a for a in E.get_all_level_actors() if a.get_class().get_name() == "BP_Cavalry_C"], key=lambda a: a.get_actor_label())
    for a in cav[4:]:
        for k in ("Horse", "Rider"):
            b = a.get_editor_property(k)
            if b:
                for ch in b.get_attached_actors(): E.destroy_actor(ch)
                E.destroy_actor(b)
        for ch in a.get_attached_actors(): E.destroy_actor(ch)
        E.destroy_actor(a); out["removed"] += 1
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith("HorseLane_"):
            a.root_component.set_mobility(unreal.ComponentMobility.MOVABLE); l = a.get_actor_location(); a.set_actor_location(V(l.x, l.y, -100.0), False, False); out["lanes"] += 1
    return out
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("cavalry", cavalry)
    L.load_level("/Game/TUM/Maps/M_Cut_WarField"); step("level", level); L.save_current_level(); return res
