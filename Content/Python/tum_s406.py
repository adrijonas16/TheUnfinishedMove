# War polish: no invisible walls, realistic jump, GTA-style round minimap (rotates with the camera, centred on you, goal blip on the edge)
import unreal, importlib, traceback, math
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; UI = f"{R}/Materials/UI"; HUD = f"{R}/Core/BP_ObjectiveHUD"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
MPC = f"{UI}/MPC_Minimap"
HLSL = r"""
float2 st = float2((UV.x - 0.5) * 2.0, (0.5 - UV.y) * 2.0);
st = float2(st.x * FX, st.y * FY);
float r = length(st);
float c = cos(A); float s = sin(A);
float dx = (st.y * c - st.x * s) * Rad;
float dy = (st.y * s + st.x * c) * Rad;
float2 m = float2(PU + dy, PV - dx);
float3 col = Texture2DSample(Tex, TexSampler, m).rgb * 1.25;
float outside = step(1.0, max(abs(m.x - 0.5), abs(m.y - 0.5)) * 2.0);
col = lerp(col, float3(0.06, 0.06, 0.07), outside);
float ring = smoothstep(0.90, 0.935, r);
col = lerp(col, float3(0.10, 0.09, 0.08), ring);
float a = 1.0 - smoothstep(0.975, 1.0, r);
return float4(col, a * 0.96);
"""

def walls_and_jump():
    out = {}
    for a in E.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor): continue
        c = a.static_mesh_component
        hid = a.get_editor_property("hidden") or not c.is_visible()
        if hid and c.get_collision_profile_name() != "NoCollision":
            c.set_collision_profile_name("NoCollision"); a.set_actor_enable_collision(False); out.setdefault("unblocked", []).append(a.get_actor_label())
        if a.get_actor_label().startswith("Stone_"):
            o, e = a.get_actor_bounds(False)
            if e.z * 2 < 60: c.set_collision_profile_name("NoCollision"); a.set_actor_enable_collision(False)
    b = EAL.load_asset(f"{R}/Core/BP_TUMCharacter"); cdo = unreal.get_default_object(b.generated_class())
    cm = cdo.get_editor_property("character_movement")
    cm.set_editor_property("jump_z_velocity", 430.0); cm.set_editor_property("gravity_scale", 1.3); cm.set_editor_property("air_control", 0.25)
    EAL.save_loaded_asset(b, False); out["jump"] = "430 @ g1.3 (~55 cm)"
    L.save_current_level(); return out

def materials():
    if not EAL.does_asset_exist(MPC):
        mpc = AT.create_asset("MPC_Minimap", UI, unreal.MaterialParameterCollection, unreal.MaterialParameterCollectionFactoryNew())
    mpc = EAL.load_asset(MPC)
    sp = []
    for n, v in (("PU", 0.5), ("PV", 0.5), ("A", 0.0), ("Rad", 0.25), ("FX", 1.0), ("FY", 1.0)):
        p = unreal.CollectionScalarParameter(); p.set_editor_property("parameter_name", n); p.set_editor_property("default_value", v); sp.append(p)
    mpc.set_editor_property("scalar_parameters", sp); EAL.save_loaded_asset(mpc, False)
    p = f"{UI}/M_MinimapGTA"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_MinimapGTA", UI, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("two_sided", True)
    try: m.set_editor_property("disable_depth_test", True)
    except Exception: pass
    cu = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -200, 0)
    cu.set_editor_property("code", HLSL); cu.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT4)
    names = ["UV", "Tex", "PU", "PV", "A", "Rad", "FX", "FY"]
    ins = []
    for n in names:
        ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    cu.set_editor_property("inputs", ins)
    uv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -700, -200)
    tex = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -700, -100); tex.set_editor_property("parameter_name", "Map")
    tex.set_editor_property("texture", EAL.load_asset("/Engine/EngineResources/DefaultTexture"))
    MEL.connect_material_expressions(uv, "", cu, "UV"); MEL.connect_material_expressions(tex, "", cu, "Tex")
    for i, n in enumerate(["PU", "PV", "A", "Rad", "FX", "FY"]):
        cp = MEL.create_material_expression(m, unreal.MaterialExpressionCollectionParameter, -700, i * 80)
        cp.set_editor_property("collection", mpc); cp.set_editor_property("parameter_name", n)
        MEL.connect_material_expressions(cp, "", cu, n)
    rgb = MEL.create_material_expression(m, unreal.MaterialExpressionComponentMask, 100, -50)
    rgb.set_editor_property("r", True); rgb.set_editor_property("g", True); rgb.set_editor_property("b", True); rgb.set_editor_property("a", False)
    al = MEL.create_material_expression(m, unreal.MaterialExpressionComponentMask, 100, 80)
    al.set_editor_property("r", False); al.set_editor_property("g", False); al.set_editor_property("b", False); al.set_editor_property("a", True)
    MEL.connect_material_expressions(cu, "", rgb, ""); MEL.connect_material_expressions(cu, "", al, "")
    MEL.connect_material_property(rgb, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(al, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False)
    out = []
    for mp in ("War", "Factory", "Cliff", "Dragon"):
        ip = f"{UI}/MI_MiniGTA_{mp}"
        mi = EAL.load_asset(ip) if EAL.does_asset_exist(ip) else AT.create_asset(f"MI_MiniGTA_{mp}", UI, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        MEL.set_material_instance_parent(mi, m); MEL.set_material_instance_texture_parameter_value(mi, "Map", EAL.load_asset(f"{UI}/T_Map_{mp}")); EAL.save_loaded_asset(mi, False); out.append(ip)
    return out

def vec(base, *terms):
    comps = []
    for ax in ("x", "y", "z"):
        s = f"(.{ax} {base})"
        for v, k in terms: s = f"(+ {s} (* (.{ax} {v}) {k}))"
        comps.append(s)
    return f"(Math|Vector|MakeVector {comps[0]} {comps[1]} {comps[2]})"
def setp(n, v): return f'  (Rendering|Material|SetScalarParameterValue :Collection mpc :ParameterName "{n}" :ParameterValue {v})\n'

def hud():
    TG.ensure_vars(HUD, [("Stage", "int"), ("bFactory", "bool"), ("Dist", "float"), ("Drop", "float"), ("StartDist", "float"),
                         ("MapCX", "float"), ("MapCY", "float"), ("MapHalf", "float"), ("MapView", "float")],
                   objs=[("GoalActor", unreal.Actor.static_class()), ("MapMPC", unreal.MaterialParameterCollection.static_class())])
    hints = "\n".join(f'  (for h{n} (Actor|GetAllActorswithTag :Tag "HUDS{n}") (Rendering|SetActorHiddenInGame :self h{n} :bNewHidden (not (== {g("Stage")} {n}))))' for n in range(4))
    goals = "\n".join(f'  (for q{n} (Actor|GetAllActorswithTag :Tag "GoalS{n}") (if (== {g("Stage")} {n}) (Variables|Default|SetGoalActor q{n})))' for n in range(4))
    GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
    S3 = lambda k: f"(Math|Vector|MakeVector {k} {k} {k})"
    code = f"""
(event EventBeginPlay
  (Variables|Default|SetStage 0)
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
  (bind dia (* hw 0.40))
  (bind c {vec('cl', ('f', g('Dist')), ('u', '(* hw -0.30)'), ('rv', '(* hw -0.74)'))})
  (bind pp (Transformation|GetActorLocation :self {PL}))
  (bind gl (Transformation|GetActorLocation :self {g('GoalActor')}))
  (bind cy (* (.z cr) 0.0174533))
  (bind mpc {g('MapMPC')})
{setp('PU', f"(+ 0.5 (/ (- (.y pp) {g('MapCY')}) (* 2.0 {g('MapHalf')})))")}{setp('PV', f"(- 0.5 (/ (- (.x pp) {g('MapCX')}) (* 2.0 {g('MapHalf')})))")}{setp('A', 'cy')}{setp('Rad', f"(/ {g('MapView')} (* 2.0 {g('MapHalf')}))")}
  (for md (Actor|GetAllActorswithTag :Tag "MMDisc")
    (Transformation|SetActorLocationAndRotation :self md :NewLocation c :NewRotation (Math|Rotator|CombineRotators :A (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 90.0 :Yaw 0.0) :B cr) :bTeleport true)
    (Transformation|SetActorScale3D :self md :NewScale3D (Math|Vector|MakeVector (/ dia 100.0) (/ dia 100.0) 1.0)))
  (bind rx (- (.x gl) (.x pp)))
  (bind ry (- (.y gl) (.y pp)))
  (bind gf (/ (+ (* rx (Math|Trig|Cos(Radians) cy)) (* ry (Math|Trig|Sin(Radians) cy))) {g('MapView')}))
  (bind gr (/ (+ (* rx (- 0.0 (Math|Trig|Sin(Radians) cy))) (* ry (Math|Trig|Cos(Radians) cy))) {g('MapView')}))
  (bind gk (Math|Float|Min(Float) 1.0 (/ 0.86 (+ (Math|Vector|VectorLength (Math|Vector|MakeVector gf gr 0.0)) 0.0001))))
  (for mb (Actor|GetAllActorswithTag :Tag "MMBlip")
    (Transformation|SetActorLocationAndRotation :self mb :NewLocation {vec('c', ('rv', '(* (* gr gk) (* dia 0.5))'), ('u', '(* (* gf gk) (* dia 0.5))'), ('f', '-0.06'))} :NewRotation cr :bTeleport true)
    (Transformation|SetActorScale3D :self mb :NewScale3D {S3('(/ (* hw 0.020) 100.0)')}))
  (for ma (Actor|GetAllActorswithTag :Tag "MMArrow")
    (Transformation|SetActorLocationAndRotation :self ma :NewLocation {vec('c', ('f', '-0.07'))} :NewRotation (Math|Rotator|CombineRotators :A (Math|Rotator|MakeRotator :Roll (- (.z (Transformation|GetActorRotation :self {PL})) (.z cr)) :Pitch 0.0 :Yaw 0.0) :B cr) :bTeleport true)
    (Transformation|SetActorScale3D :self ma :NewScale3D (Math|Vector|MakeVector 0.0005 (/ (* hw 0.016) 100.0) (/ (* hw 0.026) 100.0)))))
"""
    r = TG.run(HUD, code, events=["Setup"], clear=True)
    b = EAL.load_asset(HUD)
    for n in ("bFactory", "MapCX", "MapCY", "MapHalf", "MapView", "MapMPC"): BEL.set_blueprint_variable_instance_editable(b, n, True)
    BEL.compile_blueprint(b); cdo = unreal.get_default_object(b.generated_class())
    cdo.set_editor_property("Dist", 70.0); cdo.set_editor_property("Drop", -27.0); cdo.set_editor_property("MapHalf", 5000.0); cdo.set_editor_property("MapView", 2600.0)
    cdo.set_editor_property("MapMPC", EAL.load_asset(MPC))
    EAL.save_loaded_asset(b, False); return str(r)[:300]

def place_map(mapname, view):
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(("Map_", "MM_")): E.destroy_actor(a)
    def m(shape, mat, tag, prio):
        a = E.spawn_actor_from_class(unreal.StaticMeshActor, V(0, 0, -9000), unreal.Rotator())
        c = a.static_mesh_component; c.set_mobility(unreal.ComponentMobility.MOVABLE); c.set_static_mesh(EAL.load_asset(f"/Engine/BasicShapes/{shape}"))
        c.set_material(0, mat); c.set_collision_profile_name("NoCollision"); c.set_cast_shadow(False); a.set_actor_enable_collision(False)
        try: c.set_editor_property("translucency_sort_priority", prio)
        except Exception: pass
        a.tags = [tag]; a.set_actor_label(f"MM_{tag}"); a.set_folder_path("UI/Map")
    m("Plane", EAL.load_asset(f"{UI}/MI_MiniGTA_{mapname}"), "MMDisc", 1)
    m("Sphere", EAL.load_asset(f"{UI}/MI_Map_Goal"), "MMBlip", 2)
    m("Cone", EAL.load_asset(f"{UI}/MI_Map_You"), "MMArrow", 3)
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "ObjectiveHUD":
            a.set_editor_property("MapView", float(view)); a.set_editor_property("MapMPC", EAL.load_asset(MPC))
    L.save_current_level(); return "ok"

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField"); step("walls", walls_and_jump)
    step("materials", materials); step("hud", hud)
    for mp, nm, view in (("M_Cut_WarField", "War", 2600), ("M_FactoryHub", "Factory", 2600), ("M_Cut_Cliff", "Cliff", 2200), ("M_Cut_Dragon", "Dragon", 6000)):
        L.load_level(f"{R}/Maps/{mp}"); step(mp, lambda: place_map(nm, view))
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    return res
