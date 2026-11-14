# War, AC-style: catapult stones stay on the ground (solid) and hurt, knights hurt, health that regenerates,
# a screen-space HUD (health + objective top-left, compass with goal marker on top, minimap bottom-left).
import unreal, importlib, traceback, inspect
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
import tum_s364b as S; importlib.reload(S)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
SML = unreal.EditorStaticMeshLibrary
E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"; UI = f"{R}/Materials/UI"
CH, OH, TH, MPC = f"{R}/Core/BP_TUMCharacter", f"{R}/Core/BP_ObjectiveHUD", f"{R}/Core/BP_TUMHUD", f"{UI}/MPC_Minimap"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
NP = 10
GA = f"{R}/Characters/Gael/Anim"
def col(r, gg, b, a): return f"(Utilities|Struct|MakeLinearColor :R {r} :G {gg} :B {b} :A {a})"
BLACK = col(0.0, 0.0, 0.0, 1.0)
def hurt(dmg):
    return (f"(Class|BPTUMCharacter|SetHealth :self ch :Health (- (Class|BPTUMCharacter|GetHealth :self ch) {dmg}))\n"
            f"              (Class|BPTUMCharacter|SetLastHit :self ch :LastHit (Utilities|Time|GetGameTimeinSeconds))")

# ---------------------------------------------------------------- catapult: a pool of stones that stay where they land
def catapult_bp():
    p = f"{WB}/BP_Catapult"
    TG.ensure_vars(p, [(n, "float") for n in ("T", "Next", "OX", "OY", "OZ", "TX", "TY", "TZ", "RockZ")] + [("Fly", "bool"), ("bOpener", "bool"), ("Shots", "int"), ("Idx", "int"), ("bLoaded", "bool")],
                   objs=[("Crater", unreal.Actor.static_class()), ("Rock", unreal.StaticMeshActor.static_class()), ("Launch", unreal.SoundBase.static_class()), ("Impact", unreal.SoundBase.static_class()),
                         ("Dust", unreal.NiagaraSystem.static_class()), ("Trail", unreal.NiagaraSystem.static_class()), ("Cat", unreal.StaticMeshActor.static_class())]
                        + [(f"Pool{k}", unreal.StaticMeshActor.static_class()) for k in range(NP)])
    pick = "\n".join(f"        (if (== {g('Idx')} {k}) (Variables|Default|SetRock {g(f'Pool{k}')}))" for k in range(NP))
    code = f"""
(event EventTick (DeltaSeconds)
  (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
  (bind me (Transformation|GetActorLocation))
  (if {g('Fly')}
    (bind a (/ {g('T')} 2.4))
    (bind h (* (Math|Trig|Sin(Radians) (* a 3.14159)) 2600.0))
    (Transformation|SetActorLocation :self {g('Rock')} :NewLocation (Math|Vector|MakeVector (+ {g('OX')} (* (- {g('TX')} {g('OX')}) a)) (+ {g('OY')} (* (- {g('TY')} {g('OY')}) a)) (+ (+ {g('OZ')} (* (- {g('TZ')} {g('OZ')}) a)) h)) :bTeleport true)
    (Transformation|AddActorLocalRotation :self {g('Rock')} :DeltaRotation (Math|Rotator|MakeRotator :Roll (* DeltaSeconds 200.0) :Pitch (* DeltaSeconds 300.0) :Yaw 0.0))
    (if (> a 1.0)
      (Variables|Default|SetFly false)
      (Variables|Default|SetT 0.0)
      (Variables|Default|SetNext (Math|Random|RandomFloatinRange :Min 4.0 :Max 7.5))
      (bind tg (Math|Vector|MakeVector {g('TX')} {g('TY')} {g('TZ')}))
      (Transformation|SetActorLocation :self {g('Rock')} :NewLocation tg :bTeleport true)
      (Audio|PlaySoundatLocation :Sound {g('Impact')} :Location tg :VolumeMultiplier 1.3 :PitchMultiplier (Math|Random|RandomFloatinRange :Min 0.85 :Max 1.1))
      (Niagara|SpawnSystematLocation :SystemTemplate {g('Dust')} :Location tg :Scale (Math|Vector|MakeVector 1.6 1.6 1.6))
      (Transformation|SetActorLocation :self {g('Crater')} :NewLocation (Math|Vector|MakeVector {g('TX')} {g('TY')} 0.0) :bTeleport true)
      (Variables|Default|SetShots (+ {g('Shots')} 1))
      (bind pp (Transformation|GetActorLocation :self {PL}))
      (bind dd (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pp) {g('TX')}) (- (.y pp) {g('TY')}) 0.0)))
      (if (< dd 280.0)
        (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object {PL})
          (:then
              (Character|LaunchCharacter :self ch :LaunchVelocity (Math|Vector|MakeVector (* (- (.x pp) {g('TX')}) 1.5) (* (- (.y pp) {g('TY')}) 1.5) 280.0) :bXYOverride true :bZOverride true)
              {hurt("(+ 25.0 (* 45.0 (- 1.0 (/ dd 280.0))))")})
          (:CastFailed))))
    (else
      (if (and (> {g('T')} 1.6) (not {g('Loaded')}))
        (Variables|Default|SetLoaded true)
        (Variables|Default|SetIdx (+ {g('Idx')} 1))
        (if (> {g('Idx')} {NP - 1}) (Variables|Default|SetIdx 0))
{pick}
        (Transformation|SetActorLocation :self {g('Rock')} :NewLocation (Math|Vector|MakeVector (.x me) (.y me) (+ (.z me) 330.0)) :bTeleport true))
      (if (> {g('T')} {g('Next')})
        (Variables|Default|SetFly true)
        (Variables|Default|SetLoaded false)
        (Variables|Default|SetT 0.0)
        (bind pl (Transformation|GetActorLocation :self {PL}))
        (if (and {g('Opener')} (== {g('Shots')} 0))
          (Variables|Default|SetTX (+ (.x pl) 420.0))
          (Variables|Default|SetTY (+ (.y pl) 160.0))
          (else
            (Variables|Default|SetTX (+ (.x pl) (Math|Random|RandomFloatinRange :Min 450.0 :Max 1500.0)))
            (Variables|Default|SetTY (+ (.y pl) (Math|Random|RandomFloatinRange :Min -800.0 :Max 800.0)))))
        (Variables|Default|SetTZ {g('RockZ')})
        (Variables|Default|SetOX (.x me))
        (Variables|Default|SetOY (.y me))
        (Variables|Default|SetOZ (+ (.z me) 330.0))
        (Niagara|SpawnSystematLocation :SystemTemplate {g('Dust')} :Location me)
        (Niagara|SpawnSystemAttached :SystemTemplate {g('Trail')} :AttachToComponent (Class|StaticMeshActor|GetStaticMeshComponent :self {g('Rock')}) :bAutoDestroy true)
        (Audio|PlaySoundatLocation :Sound {g('Launch')} :Location me :VolumeMultiplier 1.0)))))
"""
    r = TG.run(p, code, clear=True)
    S.editable(p, ["Rock", "Launch", "Impact", "Dust", "Trail", "Cat", "Next", "Crater", "bOpener", "RockZ", "bLoaded"] + [f"Pool{k}" for k in range(NP)], {"Next": 4.0, "bLoaded": True, "RockZ": 35.0})
    return str(r)[:200]

def stones_level():
    out = []
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("CatRock_") and "_P" in a.get_actor_label(): E.destroy_actor(a)
    for ctl in [a for a in E.get_all_level_actors() if a.get_actor_label().startswith("Catapult_") and a.get_actor_label().endswith("_Ctl")]:
        rock = ctl.get_editor_property("Rock"); mesh = rock.static_mesh_component.static_mesh; sc = rock.get_actor_scale3d()
        if SML.get_simple_collision_count(mesh) == 0:
            bs = mesh.get_editor_property("body_setup"); bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            mesh.set_editor_property("body_setup", bs); EAL.save_loaded_asset(mesh, False)
        bb = mesh.get_bounding_box(); cl = ctl.get_actor_location()
        rockz = (M.ground_z(cl.x, cl.y) or 0.0) - bb.min.z * sc.z - 10.0
        pools = [rock]
        for k in range(1, NP):
            s = E.spawn_actor_from_object(mesh, V(cl.x, cl.y, -20000 - k * 300)); s.set_actor_scale3d(sc)
            s.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            s.set_actor_label(f"{rock.get_actor_label()}_P{k}"); s.set_folder_path("Art/War/Battle/Catapults"); pools.append(s)
        for k, s in enumerate(pools):
            s.static_mesh_component.set_collision_profile_name("BlockAll"); s.set_actor_enable_collision(True)
            ctl.set_editor_property(f"Pool{k}", s)
        ctl.set_editor_property("RockZ", float(rockz)); ctl.set_editor_property("bLoaded", True)
        out.append([ctl.get_actor_label(), round(rockz)])
    return out

# ---------------------------------------------------------------- knights: their strike hurts; crouching halves how far they see you
def knight_bp():
    import tum_s394 as K; importlib.reload(K)
    src = inspect.getsource(K.knight)
    a = "(Utilities|Casting|CastToCharacter :Object {PL})"
    b_ = ":bXYOverride true :bZOverride true))\n            (:CastFailed)"
    assert src.count(a) == 1 and src.count(b_) == 1, (src.count(a), src.count(b_))
    src = src.replace(a, "(Utilities|Casting|CastToBP_TUMCharacter :Object {PL})")
    src = src.replace(b_, ":bXYOverride true :bZOverride true)\n              " + hurt("22.0").replace("{", "{{").replace("}", "}}") + ")\n            (:CastFailed)")
    sight = "(if (and los (< d {g('Sight')}))"
    assert src.count(sight) == 1
    src = src.replace(sight, "(if (and los (< d (* {g('Sight')} (select (Class|Character|GetIsCrouched :self {PL}) 0.55 1.0))))")
    ns = dict(K.__dict__); exec(src, ns); return ns["knight"]()

# ---------------------------------------------------------------- screen-space minimap material (UI domain) with goal blip and player arrow
HLSL = r"""
float2 st = float2((UV.x - 0.5) * 2.0, (0.5 - UV.y) * 2.0);
float r = length(st);
float c = cos(A); float s = sin(A);
float dx = (st.y * c - st.x * s) * Rad;
float dy = (st.y * s + st.x * c) * Rad;
float2 m = float2(PU + dy, PV - dx);
float3 col = Texture2DSample(Tex, TexSampler, m).rgb * 1.25;
float outside = step(1.0, max(abs(m.x - 0.5), abs(m.y - 0.5)) * 2.0);
col = lerp(col, float3(0.06, 0.06, 0.07), outside);
float ga = -(GV - PV) / Rad; float gb = (GU - PU) / Rad;
float2 gs = float2(-s * ga + c * gb, c * ga + s * gb);
float gl = length(gs); gs *= min(1.0, 0.82 / max(gl, 0.0001));
float gd = length(st - gs);
col = lerp(col, float3(0.04, 0.03, 0.02), 1.0 - smoothstep(0.085, 0.10, gd));
col = lerp(col, float3(1.0, 0.62, 0.18), 1.0 - smoothstep(0.06, 0.075, gd));
float2 dd = float2(sin(H), cos(H)); float2 rr = float2(cos(H), -sin(H));
float ly = dot(st, dd); float lx = dot(st, rr);
float tri = step(-0.07, ly) * step(ly, 0.12) * step(abs(lx), (0.12 - ly) * 0.5);
float tri2 = step(-0.09, ly) * step(ly, 0.15) * step(abs(lx), (0.15 - ly) * 0.55);
col = lerp(col, float3(0.02, 0.02, 0.02), tri2);
col = lerp(col, float3(0.96, 0.96, 0.92), tri);
float ring = smoothstep(0.90, 0.935, r);
col = lerp(col, float3(0.10, 0.09, 0.08), ring);
float al = 1.0 - smoothstep(0.975, 1.0, r);
return float4(col, al * 0.92);
"""
def minimap_ui():
    mpc = EAL.load_asset(MPC); sp = list(mpc.get_editor_property("scalar_parameters")); have = {str(p.get_editor_property("parameter_name")) for p in sp}
    for n, v in (("GU", 0.5), ("GV", 0.5), ("H", 0.0)):
        if n not in have:
            p = unreal.CollectionScalarParameter(); p.set_editor_property("parameter_name", n); p.set_editor_property("default_value", v); sp.append(p)
    mpc.set_editor_property("scalar_parameters", sp); EAL.save_loaded_asset(mpc, False)
    p = f"{UI}/M_MinimapUI"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_MinimapUI", UI, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_UI); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    cu = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -200, 0)
    cu.set_editor_property("code", HLSL); cu.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT4)
    names = ["UV", "Tex", "PU", "PV", "A", "Rad", "GU", "GV", "H"]
    ins = []
    for n in names:
        ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    cu.set_editor_property("inputs", ins)
    uv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -700, -200)
    tex = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -700, -100); tex.set_editor_property("parameter_name", "Map")
    tex.set_editor_property("texture", EAL.load_asset("/Engine/EngineResources/DefaultTexture"))
    MEL.connect_material_expressions(uv, "", cu, "UV"); MEL.connect_material_expressions(tex, "", cu, "Tex")
    for i, n in enumerate(names[2:]):
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
    for mp in ("War", "Factory", "Cliff", "Dragon"):
        ip = f"{UI}/MI_MiniUI_{mp}"
        mi = EAL.load_asset(ip) if EAL.does_asset_exist(ip) else AT.create_asset(f"MI_MiniUI_{mp}", UI, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        MEL.set_material_instance_parent(mi, m); MEL.set_material_instance_texture_parameter_value(mi, "Map", EAL.load_asset(f"{UI}/T_Map_{mp}")); EAL.save_loaded_asset(mi, False)
    return "ok"

# ---------------------------------------------------------------- the HUD class (Canvas: fixed to the screen, cannot lag behind the camera)
def T(text, x, y, s, c):
    F = g("HudFont")
    return (f"(HUD|DrawText :Text {text} :TextColor {col(0.0, 0.0, 0.0, 0.8)} :ScreenX (+ {x} (* u 2.0)) :ScreenY (+ {y} (* u 2.0)) :Font {F} :Scale {s} :bScalePosition false)\n"
            f"    (HUD|DrawText :Text {text} :TextColor {c} :ScreenX {x} :ScreenY {y} :Font {F} :Scale {s} :bScalePosition false)")
def R_(c, x, y, w, h): return f"(HUD|DrawRect :RectColor {c} :ScreenX {x} :ScreenY {y} :ScreenW {w} :ScreenH {h})"
AMBER = col(1.0, 0.66, 0.24, 1.0); WHITE = col(0.96, 0.95, 0.9, 1.0); GREY = col(0.78, 0.78, 0.76, 0.95)
def setp(n, v): return f'      (Rendering|Material|SetScalarParameterValue :Collection {g("MPC")} :ParameterName "{n}" :ParameterValue {v})\n'

def hud_bp():
    if not EAL.does_asset_exist(TH): BT.create(f"{R}/Core", "BP_TUMHUD", unreal.HUD.static_class())
    TG.ensure_vars(OH, [], objs=[("MiniUI", unreal.MaterialInterface.static_class())])
    ob = EAL.load_asset(OH); BEL.set_blueprint_variable_instance_editable(ob, "MiniUI", True); BEL.compile_blueprint(ob); EAL.save_loaded_asset(ob, False)
    TG.ensure_vars(TH, [("bOn", "bool"), ("bDying", "bool"), ("W", "float"), ("H", "float"), ("Objective", "string"), ("Hint1", "string"), ("Hint2", "string"), ("Hint3", "string"), ("CA", "int"), ("Dbg", "int")],
                   objs=[("Ch", EAL.load_asset(CH).generated_class()), ("Obj", ob.generated_class()), ("HudFont", unreal.Font.static_class()), ("MPC", unreal.MaterialParameterCollection.static_class()), ("CrouchWalk", unreal.AnimSequence.static_class()), ("CrouchIdle", unreal.AnimSequence.static_class())])
    ch = "(Variables|Default|GetCh)"; ob_ = "(Variables|Default|GetObj)"
    labels = []
    for name, yaw, big in (("N", 0, 1), ("NE", 45, 0), ("E", 90, 1), ("SE", 135, 0), ("S", 180, 1), ("SW", 225, 0), ("W", 270, 1), ("NW", 315, 0)):
        v = f"d{name}"
        labels.append(f"""    (bind {v} (Math|Rotator|NormalizeAxis (- {yaw}.0 cam)))
    (if (and (< {v} 86.0) (> {v} -86.0))
      {T(f'"{name}"', f"(- (+ cx (* (/ {v} 90.0) half)) (* u {7.0 if big else 10.0}))", "(- cy (* u 3.0))", f"(* u {1.9 if big else 1.3})", col(0.96, 0.95, 0.9, f"(- 1.0 (/ (* {v} {v}) 7744.0))"))})""")
    labels = "\n".join(labels)
    DISTTXT = T('(Utilities|String|Append (Utilities|String|ToString(Integer) (Math|Float|Truncate (/ (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x gl) (.x pp)) (- (.y gl) (.y pp)) 0.0)) 100.0))) " m")', "(- xg (* u 18.0))", "(+ cy (* u 28.0))", "(* u 1.5)", AMBER)
    code = f"""
(event EventBeginPlay
  (Variables|Default|SetOn false)
  (Variables|Default|SetDying false)
  (for a (Actor|GetAllActorswithTag :Tag "ACHUD") (Variables|Default|SetOn true)))

(event EventTick (DeltaSeconds)
  (for o (Actor|GetAllActorswithTag :Tag "ObjHUD")
    (bind oh (Utilities|Casting|CastToBP_ObjectiveHUD :Object o)
      (:then (Variables|Default|SetObj oh))
      (:CastFailed)))
  (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object {PL})
    (:then
      (Variables|Default|SetCh ch)
      (bind now (Utilities|Time|GetGameTimeinSeconds))
      (bind hp (Class|BPTUMCharacter|GetHealth :self ch))
      (bind mesh (Class|Character|GetMesh :self ch))
      (if (and (Class|Character|GetIsCrouched :self ch) (not (Class|BPTUMCharacter|GetSliding :self ch)))
        (bind cv (Transformation|GetVelocity :self ch))
        (bind msp (Math|Vector|VectorLength (Math|Vector|MakeVector (.x cv) (.y cv) 0.0)))
        (if (> msp 25.0)
          (if (not (== {g('CA')} 1))
            (Variables|Default|SetCA 1)
            (Components|Animation|PlayAnimation :self mesh :NewAnimToPlay {g('CrouchWalk')} :bLooping true))
          (Components|Animation|SetPlayRate :self mesh :Rate (Math|Float|Clamp(Float) (/ msp 170.0) 0.6 1.4))
          (else
            (if (not (== {g('CA')} 2))
              (Variables|Default|SetCA 2)
              (Components|Animation|SetPlayRate :self mesh :Rate 1.0)
              (Components|Animation|PlayAnimation :self mesh :NewAnimToPlay {g('CrouchIdle')} :bLooping true))))
        (else (Variables|Default|SetCA 0)))
      (if (and (> (- now (Class|BPTUMCharacter|GetLastHit :self ch)) 5.0) (< hp 100.0))
        (Class|BPTUMCharacter|SetHealth :self ch :Health (Math|Float|Min(Float) 100.0 (+ hp (* DeltaSeconds 9.0)))))
      (if (and {g('On')} (and (< hp 0.5) (not {g('Dying')})))
        (Variables|Default|SetDying true)
        (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager 0) :FromAlpha 0.0 :ToAlpha 1.0 :Duration 0.8 :Color {BLACK} :bHoldWhenFinished true)
        (Utilities|FlowControl|Delay 1.0)
        (Game|OpenLevel(byName) :LevelName (Game|GetCurrentLevelName))))
    (:CastFailed)))

(event EventReceiveDrawHUD (SizeX SizeY)
  (Variables|Default|SetW SizeX)
  (Variables|Default|SetH SizeY)
  (bind cc (Utilities|Casting|CastToBP_TUMCharacter :Object (Game|GetPlayerCharacter 0))
    (:then (Variables|Default|SetCh cc) (CallFunction|DrawAll))
    (:CastFailed)))

(event Custom|DrawAll
  (if {g('On')}
    (Variables|Default|SetDbg 2)
    (bind u (/ {g('H')} 1080.0))
    (bind w {g('W')})
    (bind hp2 (Class|BPTUMCharacter|GetHealth :self {ch}))
    (bind since (- (Utilities|Time|GetGameTimeinSeconds) (Class|BPTUMCharacter|GetLastHit :self {ch})))
    (if (< since 0.6)
      {R_(col(0.6, 0.03, 0.0, "(* (- 0.6 since) 0.6)"), "0.0", "0.0", "w", g('H'))})
    (if (< hp2 35.0)
      {R_(col(0.35, 0.0, 0.0, "(* (- 35.0 hp2) 0.006)"), "0.0", "0.0", "w", g('H'))})
    (bind x0 (* u 44.0))
    (bind y0 (* u 40.0))
    (bind bw (* u 320.0))
    {R_(col(0.0, 0.0, 0.0, 0.55), "(- x0 (* u 3.0))", "(- y0 (* u 3.0))", "(+ bw (* u 6.0))", "(* u 15.0)")}
    {R_(col(0.22, 0.05, 0.04, 0.85), "x0", "y0", "bw", "(* u 9.0)")}
    {R_(col(0.86, 0.2, 0.11, 1.0), "x0", "y0", "(* bw (/ (Math|Float|Clamp(Float) hp2 0.0 100.0) 100.0))", "(* u 9.0)")}
    {T('"OBJECTIVE"', "x0", "(+ y0 (* u 26.0))", "(* u 1.5)", AMBER)}
    {T(g('Objective'), "x0", "(+ y0 (* u 50.0))", "(* u 2.2)", WHITE)}
    {T(g('Hint1'), "x0", "(+ y0 (* u 98.0))", "(* u 1.45)", GREY)}
    {T(g('Hint2'), "x0", "(+ y0 (* u 124.0))", "(* u 1.45)", GREY)}
    {T(g('Hint3'), "x0", "(+ y0 (* u 150.0))", "(* u 1.45)", GREY)}
    (bind cx (* w 0.5))
    (bind half (* w 0.19))
    (bind cy (* u 34.0))
    {R_(col(1.0, 1.0, 1.0, 0.3), "(- cx half)", "(+ cy (* u 22.0))", "(* half 2.0)", "(* u 2.0)")}
    {R_(col(1.0, 1.0, 1.0, 0.85), "(- cx (* u 1.0))", "(+ cy (* u 14.0))", "(* u 2.0)", "(* u 12.0)")}
    (bind (crr crp cam) (Math|Rotator|BreakRotator (Camera|GetCameraRotation :self (Game|GetPlayerCameraManager 0))))
{labels}
    (if true
      (bind ga (Class|BPObjectiveHUD|GetGoalActor :self {ob_}))
      (bind pp (Transformation|GetActorLocation :self {ch}))
      (if true
        (bind gl (Transformation|GetActorLocation :self ga))
        (bind gd (Math|Rotator|NormalizeAxis (- (Math|Trig|Atan2(Degrees) (- (.y gl) (.y pp)) (- (.x gl) (.x pp))) cam)))
        (bind xg (+ cx (* (/ (Math|Float|Clamp(Float) gd -88.0 88.0) 90.0) half)))
        {R_(col(0.0, 0.0, 0.0, 0.7), "(- xg (* u 9.0))", "(- cy (* u 1.0))", "(* u 18.0)", "(* u 18.0)")}
        {R_(AMBER, "(- xg (* u 6.0))", "(+ cy (* u 2.0))", "(* u 12.0)", "(* u 12.0)")}
        {DISTTXT}
        (bind mh (Class|BPObjectiveHUD|GetMapHalf :self {ob_}))
        (bind (prr prp pyaw) (Math|Rotator|BreakRotator (Transformation|GetActorRotation :self {ch})))
        (bind mx (Class|BPObjectiveHUD|GetMapCX :self {ob_}))
        (bind my (Class|BPObjectiveHUD|GetMapCY :self {ob_}))
{setp('GU', "(+ 0.5 (/ (- (.y gl) my) (* 2.0 mh)))")}{setp('GV', "(- 0.5 (/ (- (.x gl) mx) (* 2.0 mh)))")}{setp('H', '(* (- pyaw cam) 0.0174533)')}{setp('A', '(* cam 0.0174533)')}        (HUD|DrawMaterialSimple :Material (Class|BPObjectiveHUD|GetMiniUI :self {ob_}) :ScreenX (* u 40.0) :ScreenY (- {g('H')} (* u 300.0)) :ScreenW (* u 260.0) :ScreenH (* u 260.0) :Scale 1.0 :bScalePosition false)))))
"""
    r = TG.run(TH, code, events=["DrawAll"], clear=True)
    b = EAL.load_asset(TH); cdo = unreal.get_default_object(b.generated_class())
    cdo.set_editor_property("HudFont", EAL.load_asset("/Engine/EngineFonts/Roboto"))
    cdo.set_editor_property("MPC", EAL.load_asset(MPC))
    cdo.set_editor_property("CrouchWalk", EAL.load_asset(f"{GA}/Q_Cautious_Crouch_Walk_Forward")); cdo.set_editor_property("CrouchIdle", EAL.load_asset(f"{GA}/Q_CrouchLookAroundBow"))
    cdo.set_editor_property("Objective", "Cross the battlefield to the glowing circle")
    cdo.set_editor_property("Hint1", "Stones and knights hurt you. Stay clear for a moment to heal.")
    cdo.set_editor_property("Hint2", "SHIFT   Cut Boost - knock a knight down")
    cdo.set_editor_property("Hint3", "C   Crouch, or Slide while running      SPACE   Jump")
    t = cdo.get_editor_property("primary_actor_tick"); t.set_editor_property("start_with_tick_enabled", True); cdo.set_editor_property("primary_actor_tick", t)
    EAL.save_loaded_asset(b, False)
    # every map uses the TUM game mode -> give it this HUD
    gm = EAL.load_asset(f"{R}/Core/BP_TUMGameMode"); gcdo = unreal.get_default_object(gm.generated_class())
    gcdo.set_editor_property("hud_class", b.generated_class()); EAL.save_loaded_asset(gm, False)
    ws = M.world().get_world_settings(); dgm = ws.get_editor_property("default_game_mode")
    return {"graph": str(r)[:200], "war_gm": str(dgm)}

def war_level():
    out = {"hidden": 0}
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label(); tags = [str(t) for t in a.tags]
        if lab == "ACHUD_Marker": E.destroy_actor(a); continue
        if lab.startswith("MM_") or any(t == "HUDText" or t.startswith("HUDS") for t in tags):
            if lab.startswith("HUD_"): a.tags = [unreal.Name("OldHUDText")]
            a.set_actor_hidden_in_game(True); out["hidden"] += 1
        if lab == "ObjectiveHUD":
            if "ObjHUD" not in tags: a.tags = list(a.tags) + [unreal.Name("ObjHUD")]
            a.set_editor_property("MiniUI", EAL.load_asset(f"{UI}/MI_MiniUI_War")); out["obj"] = True
    tp = E.spawn_actor_from_class(unreal.TargetPoint, V(0, 0, -9000)); tp.tags = [unreal.Name("ACHUD")]; tp.set_actor_label("ACHUD_Marker"); tp.set_folder_path("UI")
    L.save_current_level(); return out

# ---------------------------------------------------------------- crouch (C / Ctrl / pad B) and slide (crouch while running)
def crouch():
    p = f"{R}/Core/IA_Crouch"
    ia = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset("IA_Crouch", f"{R}/Core", unreal.InputAction, unreal.InputAction_Factory())
    EAL.save_loaded_asset(ia)
    imc = EAL.load_asset("/Game/Input/IMC_Default")
    data = imc.get_editor_property("default_key_mappings"); maps = [m for m in data.get_editor_property("mappings") if m.get_editor_property("action") != ia]
    for key in ("C", "LeftControl", "Gamepad_FaceButton_Right"):
        k = unreal.Key(); k.set_editor_property("key_name", key)
        m = unreal.EnhancedActionKeyMapping(); m.set_editor_property("action", ia); m.set_editor_property("key", k); maps.append(m)
    data.set_editor_property("mappings", maps); imc.set_editor_property("default_key_mappings", data); EAL.save_loaded_asset(imc, False)
    TG.ensure_vars(CH, [("bCrouchHeld", "bool"), ("bSliding", "bool")], objs=[("SlideAnim", unreal.AnimSequence.static_class())])
    b = EAL.load_asset(CH); g_ = unreal.BlueprintEditorLibrary.find_event_graph(b)
    have = [BT._get_node_info(n).type_id for n in BT.find_nodes(g_)]
    if any("IA_Crouch" in t or "OnEndCrouch" in t for t in have): return "already wired"
    for n in list(BT.find_nodes(g_)):
        t = BT._get_node_info(n).type_id
        if "DoCrouch" in t or "DoUncrouch" in t: BT.delete_node(n)
    code = """
(event Custom|DoCrouch
  (Variables|Default|SetCrouchHeld true)
  (bind cm (Variables|Character|GetCharacterMovement))
  (bind v (Transformation|GetVelocity))
  (bind sp (Math|Vector|VectorLength (Math|Vector|MakeVector (.x v) (.y v) 0.0)))
  (if (and (> sp 330.0) (and (Movement|IsMovingonGround :self cm) (not (Variables|Default|GetSliding))))
    (Variables|Default|SetSliding true)
    (Character|Crouch)
    (Components|Animation|PlayAnimation :self (Variables|Character|GetMesh) :NewAnimToPlay (Variables|Default|GetSlideAnim) :bLooping false)
    (Class|CharacterMovementComponent|SetGroundFriction :self cm :GroundFriction 0.5)
    (Class|CharacterMovementComponent|SetBrakingDecelerationWalking :self cm :BrakingDecelerationWalking 380.0)
    (bind f (Transformation|GetActorForwardVector))
    (bind ss (Math|Float|Max(Float) sp 900.0))
    (Character|LaunchCharacter :LaunchVelocity (Math|Vector|MakeVector (* (.x f) ss) (* (.y f) ss) 0.0) :bXYOverride true :bZOverride false)
    (Utilities|FlowControl|Delay 0.8)
    (Class|CharacterMovementComponent|SetGroundFriction :self cm :GroundFriction 8.0)
    (Class|CharacterMovementComponent|SetBrakingDecelerationWalking :self cm :BrakingDecelerationWalking 2000.0)
    (Variables|Default|SetSliding false)
    (if (Variables|Default|GetCrouchHeld)
      (Character|Crouch)
      (else (Character|UnCrouch)))
    (else (Character|Crouch))))

(event Custom|DoUncrouch
  (Variables|Default|SetCrouchHeld false)
  (if (not (Variables|Default|GetSliding)) (Character|UnCrouch)))

(event EventOnEndCrouch (HalfHeightAdjust ScaledHalfHeightAdjust)
  (Components|Animation|SetAnimationMode :self (Variables|Character|GetMesh) :InAnimationMode "AnimationBlueprint"))
"""
    r = TG.run(CH, code, events=["DoCrouch", "DoUncrouch"], binds=[("IA_Crouch", [("Started", "DoCrouch"), ("Completed", "DoUncrouch")])], clear=False)
    b = EAL.load_asset(CH); cdo = unreal.get_default_object(b.generated_class())
    cm = cdo.get_editor_property("character_movement")
    nav = cm.get_editor_property("nav_agent_props"); nav.set_editor_property("can_crouch", True); cm.set_editor_property("nav_agent_props", nav)
    cm.set_editor_property("max_walk_speed_crouched", 220.0); cm.set_editor_property("crouched_half_height", 58.0)
    cdo.set_editor_property("SlideAnim", EAL.load_asset(f"{GA}/Q_sliding_stumble"))
    EAL.save_loaded_asset(b, False); return str(r)[:200]

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("hud", hud_bp)
    return res
