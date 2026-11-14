# Screen HUD for every scene: Montserrat font, readable panel, chess-knight goal marker (compass + minimap),
# objective text per map/stage stored on that map's ObjectiveHUD actor.
import unreal, importlib, traceback
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
import tum_s420 as B; importlib.reload(B)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = B.EAL; BEL = B.BEL; MEL = B.MEL; AT = B.AT; E = M.E; L = M.L; V = unreal.Vector
R, UI, CH, OH, TH, MPC = B.R, B.UI, B.CH, B.OH, B.TH, B.MPC
FD = f"{R}/UI/Fonts"; ICON = f"{R}/UI/Icons/T_Icon_Knight"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
g = B.g; col = B.col; R_ = B.R_; setp = B.setp
PL = B.PL; BLACK = B.BLACK
AMBER = col(1.0, 0.70, 0.30, 1.0); WHITE = col(1.0, 1.0, 1.0, 1.0); GREY = col(0.86, 0.86, 0.84, 1.0)

def T(text, x, y, s, c, font):
    F = g(font)
    return (f"(HUD|DrawText :Text {text} :TextColor {col(0.0, 0.0, 0.0, 0.85)} :ScreenX (+ {x} (* u 1.5)) :ScreenY (+ {y} (* u 1.5)) :Font {F} :Scale {s} :bScalePosition false)\n"
            f"    (HUD|DrawText :Text {text} :TextColor {c} :ScreenX {x} :ScreenY {y} :Font {F} :Scale {s} :bScalePosition false)")

TEXTS = {
    "M_Cut_WarField": dict(Obj=["Reach the glowing circle beyond the battlefield"] * 4,
                           Hint=["Stones and knights hurt you. Stay out of reach for a moment to heal."] * 4,
                           K=[("SHIFT", "Cut Boost - knock a knight down"), ("C", "Crouch  -  while running: Slide"), ("SPACE", "Jump")], health=True, mini="War"),
    "M_FactoryHub": dict(Obj=["Follow the amber figure to the round mark", "Climb the steel beams to the catwalk", "Cut Boost up to the high ledge", "Finish the move"],
                         Hint=["Stand on the mark and look at the round window to enter the memory.", "From the mark, look at the tall window on the far wall.",
                               "Look through the narrow slit in the far wall.", "Step on one of the three marks at the chessboard, then take the way out."],
                         K=[("SPACE", "Jump"), ("SHIFT", "Cut Boost"), ("C", "Crouch  -  while running: Slide")], health=False, mini="Factory"),
    "M_Cut_Cliff": dict(Obj=["Find the hidden path across the cliff"] * 4,
                        Hint=["Stand still and look at the far stone arch to reveal it, then cross before it fades."] * 4,
                        K=[("SPACE", "Jump"), ("SHIFT", "Cut Boost"), ("C", "Crouch  -  while running: Slide")], health=False, mini="Cliff"),
    "M_Cut_Dragon": dict(Obj=["Fly with the dragon"] * 4, Hint=["Boost through every stone arch and steer around the rocks."] * 4,
                         K=[("WASD", "Steer  -  mouse to look"), ("SHIFT", "Cut Boost"), ("", "")], health=False, mini="Dragon"),
}
OVARS = [f"ObjText{i}" for i in range(4)] + [f"Hint{i}" for i in range(4)] + ["K1", "D1", "K2", "D2", "K3", "D3"]

HLSL = B.HLSL.replace(
"""col = lerp(col, float3(0.04, 0.03, 0.02), 1.0 - smoothstep(0.085, 0.10, gd));
col = lerp(col, float3(1.0, 0.62, 0.18), 1.0 - smoothstep(0.06, 0.075, gd));""",
"""float2 iuv = float2((st.x - gs.x) / 0.30 + 0.5, 0.5 - (st.y - gs.y) / 0.30);
float inb = step(0.0, iuv.x) * step(iuv.x, 1.0) * step(0.0, iuv.y) * step(iuv.y, 1.0);
float4 ic = Texture2DSample(Icon, IconSampler, saturate(iuv)) * inb;
col = lerp(col, ic.rgb, ic.a);""")

def assets():
    out = {}
    for n in ("Montserrat-Bold_Font", "Montserrat-SemiBold_Font", "Montserrat-Medium_Font"):
        f = EAL.load_asset(f"{FD}/{n}"); f.set_editor_property("legacy_font_size", 10); EAL.save_loaded_asset(f, False)
    tx = EAL.load_asset(ICON)
    tx.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI); tx.set_editor_property("never_stream", True)
    tx.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    EAL.save_loaded_asset(tx, False)
    # minimap material with the knight as goal blip
    B.HLSL = HLSL
    src = B.minimap_ui
    import inspect
    code = inspect.getsource(src)
    code = code.replace('names = ["UV", "Tex", "PU", "PV", "A", "Rad", "GU", "GV", "H"]', 'names = ["UV", "Tex", "Icon", "PU", "PV", "A", "Rad", "GU", "GV", "H"]')
    code = code.replace('for i, n in enumerate(names[2:]):', 'ic = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObject, -700, -300); ic.set_editor_property("texture", EAL.load_asset(ICON)); MEL.connect_material_expressions(ic, "", cu, "Icon")\n    for i, n in enumerate(names[3:]):')
    ns = dict(B.__dict__); ns["HLSL"] = HLSL; ns["ICON"] = ICON; exec(code, ns); out["mini"] = ns["minimap_ui"]()
    return out

_tc = [0]
def TC(text, y, sc, c, font, dx):
    _tc[0] += 1; n = _tc[0]
    return (f"(bind (tw{n} th{n}) (HUD|GetTextSize :Text {text} :Font {g(font)} :Scale {sc}))\n      "
            + T(text, f"(+ (- bcx (* tw{n} 0.5)) {dx})", y, sc, c, font))
def hud_bp():
    TG.ensure_vars(OH, [(n, "string") for n in OVARS] + [("bHealth", "bool")], objs=[("MiniUI", unreal.MaterialInterface.static_class())])
    ob = EAL.load_asset(OH)
    for n in OVARS + ["bHealth", "MiniUI"]: BEL.set_blueprint_variable_instance_editable(ob, n, True)
    BEL.compile_blueprint(ob); EAL.save_loaded_asset(ob, False)
    TG.ensure_vars(TH, [("bOn", "bool"), ("bDying", "bool"), ("W", "float"), ("H", "float"), ("CA", "int"), ("Dbg", "int"), ("LastStage", "int"), ("BannerT", "float")],
                   objs=[("Ch", EAL.load_asset(CH).generated_class()), ("Obj", ob.generated_class()), ("FTitle", unreal.Font.static_class()), ("FBody", unreal.Font.static_class()),
                         ("FSmall", unreal.Font.static_class()), ("Knight", unreal.Texture2D.static_class()), ("MPC", unreal.MaterialParameterCollection.static_class()),
                         ("CrouchWalk", unreal.AnimSequence.static_class()), ("CrouchIdle", unreal.AnimSequence.static_class())])
    ch = "(Variables|Default|GetCh)"; o = "(Variables|Default|GetObj)"
    og = lambda n: f"(Class|BPObjectiveHUD|Get{n} :self {o})"
    stage = og("Stage")
    pick = lambda base: f"(select (== {stage} 3) {og(base + '3')} (select (== {stage} 2) {og(base + '2')} (select (== {stage} 1) {og(base + '1')} {og(base + '0')})))"
    labels = []
    for name, yaw, big in (("N", 0, 1), ("NE", 45, 0), ("E", 90, 1), ("SE", 135, 0), ("S", 180, 1), ("SW", 225, 0), ("W", 270, 1), ("NW", 315, 0)):
        v = f"d{name}"
        labels.append(f"""    (bind {v} (Math|Rotator|NormalizeAxis (- {yaw}.0 cam)))
    (if (and (< {v} 86.0) (> {v} -86.0))
      {T(f'"{name}"', f"(- (+ cx (* (/ {v} 90.0) half)) (* u {7.0 if big else 10.0}))", "(- cy (* u 2.0))", f"(* u {1.6 if big else 1.1})", col(1.0, 1.0, 1.0, f"(- 1.0 (/ (* {v} {v}) 7744.0))"), "FTitle" if big else "FSmall")})""")
    labels = "\n".join(labels)
    keys_c = "\n".join(f"""      {T(og(f'K{i}'), '(- bcx (* u 260.0))', f'(+ py (* u {130 + (i - 1) * 36}.0))', '(* u 1.4)', AMBER, 'FTitle')}
      {T(og(f'D{i}'), '(- bcx (* u 120.0))', f'(+ py (* u {130 + (i - 1) * 36}.0))', '(* u 1.4)', GREY, 'FBody')}""" for i in (1, 2, 3))
    keys = "\n".join(f"""    {T(og(f'K{i}'), "x0", f"(+ y0 (* u {120 + (i - 1) * 25}.0))", "(* u 1.3)", AMBER, "FTitle")}
    {T(og(f'D{i}'), "(+ x0 (* u 84.0))", f"(+ y0 (* u {120 + (i - 1) * 25}.0))", "(* u 1.3)", GREY, "FSmall")}""" for i in (1, 2, 3))
    dist = T('(Utilities|String|Append (Utilities|String|ToString(Integer) (Math|Float|Truncate (/ (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x gl) (.x pp)) (- (.y gl) (.y pp)) 0.0)) 100.0))) " m")',
             "(- xg (* u 15.0))", "(+ cy (* u 36.0))", "(* u 1.25)", WHITE, "FTitle")
    code = f"""
(event EventBeginPlay
  (Variables|Default|SetLastStage -1)
  (Variables|Default|SetOn false)
  (Variables|Default|SetDying false)
  (for a (Actor|GetAllActorswithTag :Tag "ACHUD") (Variables|Default|SetOn true)))

(event EventTick (DeltaSeconds)
  (for oo (Actor|GetAllActorswithTag :Tag "ObjHUD")
    (bind oh (Utilities|Casting|CastToBP_ObjectiveHUD :Object oo)
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
    (Variables|Default|SetDbg 3)
    (bind u (/ {g('H')} 1080.0))
    (bind w {g('W')})
    (bind hp2 (Class|BPTUMCharacter|GetHealth :self {ch}))
    (bind since (- (Utilities|Time|GetGameTimeinSeconds) (Class|BPTUMCharacter|GetLastHit :self {ch})))
    (if (< since 0.6)
      {R_(col(0.6, 0.03, 0.0, "(* (- 0.6 since) 0.6)"), "0.0", "0.0", "w", g('H'))})
    (if (< hp2 35.0)
      {R_(col(0.35, 0.0, 0.0, "(* (- 35.0 hp2) 0.006)"), "0.0", "0.0", "w", g('H'))})
    (bind x0 (* u 48.0))
    (bind y0 (* u 44.0))
    (bind now (Utilities|Time|GetGameTimeinSeconds))
    (if {og('Health')}
      {R_(col(0.0, 0.0, 0.0, 0.55), "(- x0 (* u 3.0))", "(- y0 (* u 3.0))", "(* u 306.0)", "(* u 14.0)")}
      {R_(col(0.85, 0.16, 0.10, 1.0), "x0", "y0", "(* (* u 300.0) (/ (Math|Float|Clamp(Float) hp2 0.0 100.0) 100.0))", "(* u 8.0)")})
    {T('"P   Mission and controls"', "(* u 320.0)", f"(- {g('H')} (* u 62.0))", "(* u 1.1)", col(0.9, 0.9, 0.88, 0.75), "FSmall")}
    (bind bcx (* w 0.5))
    (bind stg {og('Stage')})
    (if (not (== stg {g('LastStage')}))
      (Variables|Default|SetLastStage stg)
      (Variables|Default|SetBannerT now))
    (bind be (- now {g('BannerT')}))
    (if (< be 7.5)
      (bind ain (Math|Float|Clamp(Float) (/ (- be 0.35) 0.6) 0.0 1.0))
      (bind aout (Math|Float|Clamp(Float) (- 7.5 be) 0.0 1.0))
      (bind bal (Math|Float|Min(Float) ain aout))
      (bind lw (* (* u 680.0) (Math|Float|Min(Float) (Math|Float|Clamp(Float) (/ be 0.5) 0.0 1.0) aout)))
      (bind by (* {g('H')} 0.21))
      {R_(col(1.0, 0.70, 0.30, "(* 0.9 aout)"), "(- bcx (* lw 0.5))", "by", "lw", "(* u 2.0)")}
      {TC('"NEW OBJECTIVE"', "(- by (* u 30.0))", "(* u 1.25)", col(1.0, 0.70, 0.30, "bal"), "FTitle", "0.0")}
      {TC(pick('ObjText'), "(+ by (* u 12.0))", "(* u 2.4)", col(1.0, 1.0, 1.0, "bal"), "FTitle", "(* (- 1.0 ain) (* u 60.0))")}
      {TC(pick('Hint'), "(+ by (* u 58.0))", "(* u 1.35)", col(0.88, 0.88, 0.86, "(* bal 0.9)"), "FBody", "(* (- 1.0 ain) (* u 30.0))")})
    (bind cx (* w 0.5))
    (bind half (* w 0.19))
    (bind cy (* u 30.0))
    {R_(col(0.0, 0.0, 0.0, 0.35), "(- cx half)", "(- cy (* u 8.0))", "(* half 2.0)", "(* u 36.0)")}
    {R_(col(1.0, 1.0, 1.0, 0.55), "(- cx half)", "(+ cy (* u 26.0))", "(* half 2.0)", "(* u 2.0)")}
    {R_(AMBER, "(- cx (* u 1.0))", "(+ cy (* u 18.0))", "(* u 2.0)", "(* u 10.0)")}
    (bind (crr crp cam) (Math|Rotator|BreakRotator (Camera|GetCameraRotation :self (Game|GetPlayerCameraManager 0))))
{labels}
    (bind ga {og('GoalActor')})
    (bind pp (Transformation|GetActorLocation :self {ch}))
    (bind mh {og('MapHalf')})
    (bind (prr prp pyaw) (Math|Rotator|BreakRotator (Transformation|GetActorRotation :self {ch})))
    (bind gl (Transformation|GetActorLocation :self ga))
{setp('H', '(* (- pyaw cam) 0.0174533)')}{setp('A', '(* cam 0.0174533)')}    (if (> (Math|Vector|VectorLength gl) 1.0)
      (bind gd (Math|Rotator|NormalizeAxis (- (Math|Trig|Atan2(Degrees) (- (.y gl) (.y pp)) (- (.x gl) (.x pp))) cam)))
      (bind xg (+ cx (* (/ (Math|Float|Clamp(Float) gd -88.0 88.0) 90.0) half)))
      (HUD|DrawTextureSimple :Texture {g('Knight')} :ScreenX (- xg (* u 24.0)) :ScreenY (- cy (* u 17.0)) :Scale (* u 0.19) :bScalePosition false)
      {dist}
{setp('GU', f"(+ 0.5 (/ (- (.y gl) {og('MapCY')}) (* 2.0 mh)))")}{setp('GV', f"(- 0.5 (/ (- (.x gl) {og('MapCX')}) (* 2.0 mh)))")}      (Variables|Default|SetDbg 4))
    (HUD|DrawMaterialSimple :Material {og('MiniUI')} :ScreenX (* u 40.0) :ScreenY (- {g('H')} (* u 300.0)) :ScreenW (* u 260.0) :ScreenH (* u 260.0) :Scale 1.0 :bScalePosition false)
    (if (Game|IsGamePaused)
      {R_(col(0.0, 0.0, 0.0, 0.7), "0.0", "0.0", "w", g('H'))}
      (bind py (* {g('H')} 0.26))
      {TC('"PAUSED"', "(- py (* u 70.0))", "(* u 1.3)", AMBER, "FTitle", "0.0")}
      {TC('"CURRENT OBJECTIVE"', "(- py (* u 20.0))", "(* u 1.1)", col(0.8, 0.8, 0.78, 1.0), "FSmall", "0.0")}
      {TC(pick('ObjText'), "(+ py (* u 8.0))", "(* u 2.6)", WHITE, "FTitle", "0.0")}
      {TC(pick('Hint'), "(+ py (* u 60.0))", "(* u 1.4)", GREY, "FBody", "0.0")}
      {R_(col(1.0, 0.70, 0.30, 0.8), "(- bcx (* u 300.0))", "(+ py (* u 104.0))", "(* u 600.0)", "(* u 2.0)")}
{keys_c}
      {TC('"SPACE  Jump        P  Resume        R  Restart scene        X  Quit"', "(+ py (* u 260.0))", "(* u 1.25)", col(0.9, 0.9, 0.88, 1.0), "FSmall", "0.0")})))
"""
    r = TG.run(TH, code, events=["DrawAll"], clear=True)
    b = EAL.load_asset(TH); cdo = unreal.get_default_object(b.generated_class())
    for k, n in (("FTitle", "Montserrat-Bold_Font"), ("FBody", "Montserrat-SemiBold_Font"), ("FSmall", "Montserrat-Medium_Font")):
        cdo.set_editor_property(k, EAL.load_asset(f"{FD}/{n}"))
    cdo.set_editor_property("Knight", EAL.load_asset(ICON)); cdo.set_editor_property("MPC", EAL.load_asset(MPC))
    cdo.set_editor_property("CrouchWalk", EAL.load_asset(f"{B.GA}/Q_Cautious_Crouch_Walk_Forward")); cdo.set_editor_property("CrouchIdle", EAL.load_asset(f"{B.GA}/Q_CrouchLookAroundBow"))
    EAL.save_loaded_asset(b, False)
    gm = EAL.load_asset(f"{R}/Core/BP_TUMGameMode"); gcdo = unreal.get_default_object(gm.generated_class())
    gcdo.set_editor_property("hud_class", b.generated_class()); BEL.compile_blueprint(gm)
    gcdo = unreal.get_default_object(gm.generated_class()); gcdo.set_editor_property("hud_class", b.generated_class()); EAL.save_loaded_asset(gm, False)
    return str(r)[:200]

def pause_inputs():
    import tum_s500 as P5; importlib.reload(P5)
    imc = EAL.load_asset("/Game/Input/IMC_Default")
    acts = {}
    for name, keys in (("IA_Pause", ("Escape", "P", "Gamepad_Special_Right")), ("IA_Restart", ("R",)), ("IA_QuitGame", ("X",))):
        a = P5.ia(name, None); a.set_editor_property("trigger_when_paused", True); EAL.save_loaded_asset(a, False); acts[a] = keys
    data = imc.get_editor_property("default_key_mappings")
    maps = [m for m in data.get_editor_property("mappings") if m.get_editor_property("action") not in acts]
    for a, keys in acts.items():
        for key in keys:
            k = unreal.Key(); k.set_editor_property("key_name", key)
            m = unreal.EnhancedActionKeyMapping(); m.set_editor_property("action", a); m.set_editor_property("key", k); maps.append(m)
    data.set_editor_property("mappings", maps); imc.set_editor_property("default_key_mappings", data); EAL.save_loaded_asset(imc, False)
    b = EAL.load_asset(CH); g_ = unreal.BlueprintEditorLibrary.find_event_graph(b)
    have = [BT._get_node_info(n).type_id for n in BT.find_nodes(g_)]
    if any("IA_Pause" in t for t in have): return "already wired"
    for n in list(BT.find_nodes(g_)):
        t = BT._get_node_info(n).type_id
        if any(k in t for k in ("DoPause", "DoRestart", "DoQuit")): BT.delete_node(n)
    code = """
(event Custom|DoPause
  (Game|SetGamePaused :bPaused (not (Game|IsGamePaused))))

(event Custom|DoRestart
  (if (Game|IsGamePaused)
    (Game|SetGamePaused :bPaused false)
    (Game|OpenLevel(byName) :LevelName (Game|GetCurrentLevelName))))

(event Custom|DoQuit
  (if (Game|IsGamePaused)
    (Game|QuitGame :SpecificPlayer (Game|GetPlayerController 0) :QuitPreference "Quit" :bIgnorePlatformRestrictions false)))
"""
    return str(TG.run(CH, code, events=["DoPause", "DoRestart", "DoQuit"],
                      binds=[("IA_Pause", [("Started", "DoPause")]), ("IA_Restart", [("Started", "DoRestart")]), ("IA_QuitGame", [("Started", "DoQuit")])], clear=False))[:200]

def rollout():
    out = {}
    for mp, t in TEXTS.items():
        L.load_level(f"{R}/Maps/{mp}"); r = {"hidden": 0}
        for a in list(E.get_all_level_actors()):
            lab = a.get_actor_label(); tags = [str(x) for x in a.tags]
            if lab == "ACHUD_Marker": E.destroy_actor(a); continue
            if lab.startswith("MM_"): a.set_actor_hidden_in_game(True); r["hidden"] += 1
            if lab.startswith("HUD_") and isinstance(a, unreal.TextRenderActor):
                a.tags = [unreal.Name("OldHUDText")]; a.set_actor_hidden_in_game(True); r["hidden"] += 1
            if lab == "ObjectiveHUD":
                if "ObjHUD" not in tags: a.tags = list(a.tags) + [unreal.Name("ObjHUD")]
                for i in range(4):
                    a.set_editor_property(f"ObjText{i}", t["Obj"][i]); a.set_editor_property(f"Hint{i}", t["Hint"][i])
                for i, (k, d) in enumerate(t["K"], 1):
                    a.set_editor_property(f"K{i}", k); a.set_editor_property(f"D{i}", d)
                a.set_editor_property("bHealth", t["health"]); a.set_editor_property("MiniUI", EAL.load_asset(f"{UI}/MI_MiniUI_{t['mini']}")); r["obj"] = True
        tp = E.spawn_actor_from_class(unreal.TargetPoint, V(0, 0, -9000)); tp.tags = [unreal.Name("ACHUD")]; tp.set_actor_label("ACHUD_Marker"); tp.set_folder_path("UI")
        L.save_current_level(); out[mp] = r
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("pause", pause_inputs); step("hud", hud_bp)
    return res
