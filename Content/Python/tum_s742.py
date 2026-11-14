# Guide (she): stops and faces you at waypoints tagged "Pause" (to speak), disappears herself at the waypoint tagged "Vanish"
# (and the figure on the platform appears), walks faster. Factory walls get a real plaster/concrete texture (the brick MI had
# no textures and showed a checker), her glow no longer blooms in the haze, story lines use the glowing text material.
import unreal, importlib, traceback
import tum_graph as TG; importlib.reload(TG)
import tum_s666 as Q
import tum_s612 as T612
import tum_fac as K; importlib.reload(K)
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; E = K.E; V = unreal.Vector; L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
R = "/Game/TUM"; GD = f"{R}/Core/BP_Guide"
GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
g = lambda n: f"(Variables|Default|Get{n})"
def code():
    mesh = f"(Class|SkeletalMeshActor|GetSkeletalMeshComponent :self {g('Body')})"
    hints = "\n".join(f'  (for h{n} (Actor|GetAllActorswithTag :Tag "HintS{n}") (Rendering|SetActorHiddenInGame :self h{n} :bNewHidden (not (== {g("Stage")} {n}))))' for n in range(4))
    starts = "\n".join(f'  (if (== {g("Stage")} {n}) (for s{n} (Actor|GetAllActorswithTag :Tag "GuideStart{n}") (Variables|Default|SetCurrent s{n}) (Transformation|SetActorLocation :NewLocation (Transformation|GetActorLocation :self s{n}) :bTeleport true)))' for n in range(4))
    face = lambda tag: f"(Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start (Math|Vector|MakeVector (.x me{tag}) (.y me{tag}) 0.0) :Target (Math|Vector|MakeVector (.x pl{tag}) (.y pl{tag}) 0.0)) :bTeleportPhysics true)"
    return f"""
(event EventBeginPlay
  (Variables|Default|SetStage 0)
  (bind gi {GP}
    (:then
      (if (Class|BPGameProgress|GetDragonDone :self gi)
        (Variables|Default|SetStage 1))
      (if (Class|BPGameProgress|GetWarDone :self gi)
        (Variables|Default|SetStage 2))
      (if (Class|BPGameProgress|GetCliffDone :self gi)
        (Variables|Default|SetStage 3))
      (CallFunction|Setup))
    (:CastFailed (CallFunction|Setup))))

(event Custom|Setup
{hints}
{starts}
  (Components|Animation|PlayAnimation :self {mesh} :NewAnimToPlay {g('IdleAnim')} :bLooping true)
  (Variables|Default|SetMoving false))

(event Custom|Vanish
  (for a (Actor|GetAllActorswithTag :Tag "MaraWalk")
    (Rendering|SetActorHiddenInGame :self a :bNewHidden true))
  (for b (Actor|GetAllActorswithTag :Tag "MaraUp")
    (Rendering|SetActorHiddenInGame :self b :bNewHidden false))
  (Utilities|FlowControl|Delay 0.9)
  (for c (Actor|GetAllActorswithTag :Tag "L_ImHere")
    (Rendering|SetActorHiddenInGame :self c :bNewHidden false))
  (Utilities|FlowControl|Delay 3.4)
  (for d (Actor|GetAllActorswithTag :Tag "L_ImHere")
    (Rendering|SetActorHiddenInGame :self d :bNewHidden true)))

(event EventTick (DeltaSeconds)
  (if (> {g('PauseLeft')} 0.0)
    (Variables|Default|SetPauseLeft (- {g('PauseLeft')} DeltaSeconds))
    (bind meP (Transformation|GetActorLocation))
    (bind plP (Transformation|GetActorLocation :self (Game|GetPlayerCharacter 0)))
    {face('P')}
    (if {g('Moving')}
      (Components|Animation|PlayAnimation :self {mesh} :NewAnimToPlay {g('IdleAnim')} :bLooping true)
      (Variables|Default|SetMoving false))
    (else
      (bind wp (Utilities|Casting|CastToBP_GuideWaypoint :Object {g('Current')})
        (:then
          (bind me (Transformation|GetActorLocation))
          (bind tgt (Transformation|GetActorLocation :self wp))
          (bind pd (Transformation|GetDistanceTo :OtherActor (Game|GetPlayerCharacter 0)))
          (bind wd (Transformation|GetDistanceTo :OtherActor wp))
          (if (and (< pd 800.0) (> wd 15.0))
            (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterptoConstant :Current me :Target tgt :DeltaTime DeltaSeconds :InterpSpeed {g('Speed')}) :bTeleport true)
            (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start (Math|Vector|MakeVector (.x me) (.y me) 0.0) :Target (Math|Vector|MakeVector (.x tgt) (.y tgt) 0.0)) :bTeleportPhysics true)
            (if (not {g('Moving')})
              (Components|Animation|PlayAnimation :self {mesh} :NewAnimToPlay {g('WalkAnim')} :bLooping true)
              (Variables|Default|SetMoving true))
            (else
              (if (<= wd 15.0)
                (if (Actor|ActorHasTag :self wp :Tag "Pause")
                  (Variables|Default|SetPauseLeft 4.6))
                (if (Actor|ActorHasTag :self wp :Tag "Vanish")
                  (CallFunction|Vanish))
                (Variables|Default|SetCurrent (Class|BPGuideWaypoint|GetNext :self wp)))
              (bind pl (Transformation|GetActorLocation :self (Game|GetPlayerCharacter 0)))
              (if (>= pd 800.0)
                {face('')})
              (if {g('Moving')}
                (Components|Animation|PlayAnimation :self {mesh} :NewAnimToPlay {g('IdleAnim')} :bLooping true)
                (Variables|Default|SetMoving false)))))
        (:CastFailed
          (if {g('Moving')}
            (Components|Animation|PlayAnimation :self {mesh} :NewAnimToPlay {g('IdleAnim')} :bLooping true)
            (Variables|Default|SetMoving false)))))))
"""
def guide_bp():
    from editor_toolset.toolsets.blueprint import BlueprintTools as BT
    TG.ensure_vars(GD, [("PauseLeft", "float")])
    bp = EAL.load_asset(GD)
    try: BT.add_event(bp, "Vanish")
    except Exception: pass
    graph = BEL.find_event_graph(bp); c = T612._resolve(GD, code()); miss = [m for m in TG.check_ids(graph, c) if not m.startswith("CallFunction|")]
    if miss or TG.balance(c): return {"aborted": miss, "balance": TG.balance(c)}
    r = Q.patched(lambda: str(TG.run(GD, c, events=["Setup", "Vanish"], clear=True))[:200])
    bp = EAL.load_asset(GD)
    for n in ("Body", "WalkAnim", "IdleAnim", "Speed"): BEL.set_blueprint_variable_instance_editable(bp, n, True)
    BEL.compile_blueprint(bp); EAL.save_loaded_asset(bp, False); return r
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a
def level():
    out = {}
    # the triplanar master cannot sample virtual textures (they render as a checker): every MI goes back to non-virtual sets
    MEL = unreal.MaterialEditingLibrary; MS = K.MS
    def copy_tex(dst, src):
        d, s_ = EAL.load_asset(f"{MS}/{dst}"), EAL.load_asset(f"{MS}/{src}")
        for k in ("BaseColor", "Normal", "ORM"): MEL.set_material_instance_texture_parameter_value(d, k, MEL.get_material_instance_texture_parameter_value(s_, k))
        EAL.save_loaded_asset(d, False)
    for dst in ("MI_W_SteelDark", "MI_W_RailPaint", "MI_W_Grate", "MI_W_RoofSheet"): copy_tex(dst, "MI_W_MetalCorroded")
    copy_tex("MI_W_FloorWet", "MI_W_FloorDirty"); MEL.set_material_instance_scalar_parameter_value(EAL.load_asset(f"{MS}/MI_W_FloorWet"), "TileSize", 420.0)
    brick, conc = EAL.load_asset(f"{MS}/MI_Bricks059"), EAL.load_asset(f"{MS}/MI_W_WallPainted"); n = 0
    for a in E.get_all_level_actors():
        if unreal.Name(K.TAG) in a.tags and isinstance(a, unreal.StaticMeshActor):
            c = a.static_mesh_component; m = c.get_material(0); nm = m.get_name() if m else ""
            if nm in ("MI_W_WallOld", "MI_W_WallDado", "MI_Bricks059"): c.set_material(0, conc if ("dado" in a.get_actor_label() or "lintel" in a.get_actor_label()) else brick); n += 1
    out["walls"] = n
    sv = find("Say_Vanish")
    if sv: sv.set_actor_location(V(4150, -480, 100), False, False); sv.set_editor_property("Radius", 340.0)
    si = find("Say_ImHere")
    if si: E.destroy_actor(si)
    for lab, tag in (("GuideWP_0_1", "Pause"), ("GuideWP_0_4", "Vanish")):
        a = find(lab)
        if a and unreal.Name(tag) not in a.tags: a.tags = list(a.tags) + [unreal.Name(tag)]
    gd = find("Guide_Mara"); gd.set_editor_property("Speed", 190.0)
    gl = find("Guide_Mara_Glow"); pc = gl.point_light_component; pc.set_intensity(650.0); pc.set_editor_property("volumetric_scattering_intensity", 0.15)
    ug = find("Mara_Up_Glow"); ug.point_light_component.set_intensity(700.0); ug.point_light_component.set_editor_property("volumetric_scattering_intensity", 0.15)
    s = find("Say_Finally"); s.set_actor_location(V(1350, -520, 100), False, False); s.set_editor_property("Radius", 780.0); s.set_editor_property("StartDelay", 3.3); s.set_editor_property("Hold", 4.4)
    tm = EAL.load_asset(f"{R}/Materials/M_TextGlow")
    for lab, size in (("L_Finally", 20.0), ("L_ImHere", 58.0), ("L_ComeUp", 46.0), ("L_How", 24.0), ("L_Seal", 18.0)):
        a = find(lab)
        if a: a.text_render.set_world_size(size); a.text_render.set_material(0, tm)
    return out
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_FactoryHub"); step("guide_bp", guide_bp)
    if not res["err"] and not isinstance(res.get("guide_bp"), dict):
        step("level", level)
        if not res["err"]: L.save_current_level()
    return res
