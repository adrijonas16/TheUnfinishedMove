# Route map on screen (start -> you -> checkpoint), soft knockback instead of sending the player back,
# hunters stop at walls, calmer artillery
import unreal, importlib, traceback, re, inspect
import tum_graph as TG; importlib.reload(TG)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; MEL = unreal.MaterialEditingLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
R = "/Game/TUM"; HUD = f"{R}/Core/BP_ObjectiveHUD"; MAT = f"{R}/Materials/UI"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
PUSH = ("(Character|LaunchCharacter :self ch :LaunchVelocity (Math|Vector|MakeVector "
        "(* (- (.x (Transformation|GetActorLocation :self ch)) (.x (Transformation|GetActorLocation))) 3.0) "
        "(* (- (.y (Transformation|GetActorLocation :self ch)) (.y (Transformation|GetActorLocation))) 3.0) 260.0) :bXYOverride true :bZOverride true)")

def materials():
    p = f"{MAT}/M_MapUnlit"
    if not EAL.does_asset_exist(p):
        m = AT.create_asset("M_MapUnlit", MAT, unreal.Material, unreal.MaterialFactoryNew())
        m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
        m.set_editor_property("two_sided", True)
        try: m.set_editor_property("disable_depth_test", True)
        except Exception: pass
        c = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -400, 0); c.set_editor_property("parameter_name", "Color")
        o = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -400, 200); o.set_editor_property("parameter_name", "Opacity"); o.set_editor_property("default_value", 1.0)
        MEL.connect_material_property(c, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        MEL.connect_material_property(o, "", unreal.MaterialProperty.MP_OPACITY)
        MEL.recompile_material(m); EAL.save_loaded_asset(m, False)
    base = EAL.load_asset(p)
    for n, col, op in (("Bar", (0.02, 0.02, 0.025), 0.6), ("Track", (0.55, 0.5, 0.42), 0.9), ("You", (1.0, 1.0, 1.0), 1.0), ("Goal", (1.0, 0.55, 0.15), 1.0)):
        ip = f"{MAT}/MI_Map_{n}"
        mi = EAL.load_asset(ip) if EAL.does_asset_exist(ip) else AT.create_asset(f"MI_Map_{n}", MAT, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        MEL.set_material_instance_parent(mi, base)
        MEL.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(*col, 1))
        MEL.set_material_instance_scalar_parameter_value(mi, "Opacity", op)
        EAL.save_loaded_asset(mi, False)
    return "ok"

def vec(base, *terms):
    """component-wise base + sum(vecvar * scalar)"""
    comps = []
    for ax in ("x", "y", "z"):
        s = f"(.{ax} {base})"
        for v, k in terms: s = f"(+ {s} (* (.{ax} {v}) {k}))"
        comps.append(s)
    return f"(Math|Vector|MakeVector {comps[0]} {comps[1]} {comps[2]})"
def place(tag, loc, scale):
    return (f'  (for m{tag} (Actor|GetAllActorswithTag :Tag "{tag}")\n'
            f'    (Transformation|SetActorLocationAndRotation :self m{tag} :NewLocation {loc} :NewRotation cr :bTeleport true)\n'
            f'    (Transformation|SetActorScale3D :self m{tag} :NewScale3D {scale}))\n')

def hud():
    TG.ensure_vars(HUD, [("Stage", "int"), ("bFactory", "bool"), ("Dist", "float"), ("Drop", "float"), ("StartDist", "float")], objs=[("GoalActor", unreal.Actor.static_class())])
    hints = "\n".join(f'  (for h{n} (Actor|GetAllActorswithTag :Tag "HUDS{n}") (Rendering|SetActorHiddenInGame :self h{n} :bNewHidden (not (== {g("Stage")} {n}))))' for n in range(4))
    goals = "\n".join(f'  (for q{n} (Actor|GetAllActorswithTag :Tag "GoalS{n}") (if (== {g("Stage")} {n}) (Variables|Default|SetGoalActor q{n})))' for n in range(4))
    GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
    S = lambda k: f"(Math|Vector|MakeVector {k} {k} {k})"
    code = f"""
(event EventBeginPlay
  (Variables|Default|SetStage 0)
  (Variables|Default|SetStartDist 0.0)
  (bind gi {GP}
    (:then
      (if {g('Factory')}
        (if (Class|BPGameProgress|GetDragonDone :self gi) (Variables|Default|SetStage 1))
        (if (Class|BPGameProgress|GetWarDone :self gi) (Variables|Default|SetStage 2))
        (if (Class|BPGameProgress|GetCliffDone :self gi) (Variables|Default|SetStage 3)))
      (CallFunction|Setup))
    (:CastFailed (CallFunction|Setup))))

(event Custom|Setup
{hints}
  (for q (Actor|GetAllActorswithTag :Tag "Goal") (Variables|Default|SetGoalActor q))
{goals})

(event EventTick (DeltaSeconds)
  (bind cm (Game|GetPlayerCameraManager 0))
  (bind cl (Camera|GetCameraLocation :self cm))
  (bind cr (Camera|GetCameraRotation :self cm))
  (bind f (Math|Vector|GetForwardVector :InRot cr))
  (bind u (Math|Vector|GetUpVector :InRot cr))
  (bind rv (Math|Vector|GetRightVector :InRot cr))
  (bind p {vec('cl', ('f', g('Dist')), ('u', g('Drop')))})
  (for t (Actor|GetAllActorswithTag :Tag "HUDText")
    (Transformation|SetActorLocationAndRotation :self t :NewLocation p :NewRotation (Math|Rotator|FindLookatRotation :Start p :Target cl) :bTeleport true))
  (bind hw (* {g('Dist')} (Math|Trig|Tan(Degrees) (* (Camera|GetFOVAngle :self cm) 0.5))))
  (bind mw (* hw 0.5))
  (bind dg (Transformation|GetDistanceTo :self {g('GoalActor')} :OtherActor {PL}))
  (if (< {g('StartDist')} 1.0) (Variables|Default|SetStartDist (+ dg 1.0)))
  (bind tt (Math|Float|MapRangeClamped :Value dg :InRangeA {g('StartDist')} :InRangeB 150.0 :OutRangeA -0.5 :OutRangeB 0.5))
  (bind c {vec('cl', ('f', g('Dist')), ('u', '(* hw 0.45)'))})
{place('MapBar', 'c', f"(Math|Vector|MakeVector 0.0005 (/ (* mw 1.12) 100.0) (/ (* hw 0.05) 100.0))")}
{place('MapTrack', 'c', f"(Math|Vector|MakeVector 0.0005 (/ mw 100.0) (/ (* hw 0.006) 100.0))")}
{place('MapStart', vec('c', ('rv', '(* mw -0.5)')), S('(/ (* hw 0.018) 100.0)'))}
{place('MapGoal', vec('c', ('rv', '(* mw 0.5)')), S('(/ (* hw 0.03) 100.0)'))}
{place('MapYou', vec('c', ('rv', '(* mw tt)'), ('f', '-0.02')), S('(/ (* hw 0.026) 100.0)'))}
  (for ml (Actor|GetAllActorswithTag :Tag "MapLabel")
    (Transformation|SetActorLocationAndRotation :self ml :NewLocation {vec('c', ('rv', '(* mw 0.5)'), ('u', '(* hw 0.05)'))} :NewRotation (Math|Rotator|FindLookatRotation :Start p :Target cl) :bTeleport true)
    (Transformation|SetActorScale3D :self ml :NewScale3D {S('(/ hw 30.0)')})))
"""
    r = TG.run(HUD, code, events=["Setup"], clear=True)
    b = EAL.load_asset(HUD); BEL.set_blueprint_variable_instance_editable(b, "bFactory", True); BEL.compile_blueprint(b)
    cdo = unreal.get_default_object(b.generated_class()); cdo.set_editor_property("Dist", 70.0); cdo.set_editor_property("Drop", -27.0)
    EAL.save_loaded_asset(b, False); return str(r)[:300]

def mover():
    import tum_s195 as W; importlib.reload(W)
    src = inspect.getsource(W.mover_bp).replace("(Class|BPTUMCharacter|Respawn :self ch)", PUSH)
    ns = dict(W.__dict__); exec(src, ns); return ns["mover_bp"]()

def hunter_art():
    import tum_s321 as H; importlib.reload(H)
    src = inspect.getsource(H.hunter)
    src = src.replace("(:then (Class|BPTUMCharacter|Respawn :self ch))", f"(:then {PUSH})")
    # stop at walls: probe 140 cm ahead at chest height
    src = src.replace("""    (bind tgt (Math|Vector|MakeVector (.x pp) (.y pp) (.z me)))""",
"""    (bind tgt (Math|Vector|MakeVector (.x pp) (.y pp) (.z me)))
    (bind dir (Math|Vector|GetForwardVector :InRot (Math|Rotator|FindLookatRotation :Start me :Target tgt)))
    (if (Collision|LineTraceByChannel :Start (Math|Vector|MakeVector (+ (.x me) (* (.x dir) 40.0)) (+ (.y me) (* (.y dir) 40.0)) (+ (.z me) 90.0)) :End (Math|Vector|MakeVector (+ (.x me) (* (.x dir) 150.0)) (+ (.y me) (* (.y dir) 150.0)) (+ (.z me) 90.0)))
      (if (> d 200.0) (Variables|Default|SetState 2)))""")
    src = src.replace('{"Speed": 430.0, "Sight": 950.0}', '{"Speed": 360.0, "Sight": 720.0}')
    ns = dict(H.__dict__); exec(src, ns); r1 = ns["hunter"]()
    a = inspect.getsource(H.artillery)
    a = a.replace(":Min 2.0 :Max 4.2", ":Min 3.0 :Max 6.0").replace(":Min 300.0 :Max 1500.0", ":Min 600.0 :Max 1700.0")
    a = a.replace(") 420.0)", ") 260.0)").replace("2.0) (* (- (.y pp) (.y loc)) 2.0) 520.0)", "1.2) (* (- (.y pp) (.y loc)) 1.2) 300.0)")
    ns = dict(H.__dict__); exec(a, ns); r2 = ns["artillery"]()
    return [r1, r2]

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("mat", materials); step("hud", hud); step("mover", mover); step("hunter_art", hunter_art)
    return res
