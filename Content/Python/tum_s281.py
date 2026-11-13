# Mara guide: an amber silhouette walks slowly ahead of the player to the next goal, and goal signs explain what to do
import unreal, importlib, traceback, math
import tum_graph as TG; importlib.reload(TG)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); BEL = unreal.BlueprintEditorLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; GW = f"{R}/Core/BP_GuideWaypoint"; GD = f"{R}/Core/BP_Guide"
GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a

def material():
    p = f"{R}/Materials/M_MaraGhost"
    if EAL.does_asset_exist(p): return "exists"
    m = AT.create_asset("M_MaraGhost", f"{R}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT); m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    fr = MEL.create_material_expression(m, unreal.MaterialExpressionFresnel, -600, 0); fr.set_editor_property("exponent", 2.5)
    c = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -600, -200); c.set_editor_property("constant", unreal.LinearColor(2.6, 1.35, 0.45, 1))
    a = MEL.create_material_expression(m, unreal.MaterialExpressionAdd, -400, 0); a.set_editor_property("const_b", 0.35); MEL.connect_material_expressions(fr, "", a, "A")
    mu = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -200, -100); MEL.connect_material_expressions(c, "", mu, "A"); MEL.connect_material_expressions(a, "", mu, "B")
    MEL.connect_material_property(mu, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    op = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -200, 150); op.set_editor_property("const_b", 0.75); MEL.connect_material_expressions(a, "", op, "A")
    MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return "ok"

def blueprints():
    if not EAL.does_asset_exist(GW): BT.create(f"{R}/Core", "BP_GuideWaypoint", unreal.Actor.static_class())
    TG.ensure_vars(GW, [], objs=[("Next", unreal.Actor.static_class())])
    b = EAL.load_asset(GW); BEL.set_blueprint_variable_instance_editable(b, "Next", True); BEL.compile_blueprint(b); EAL.save_loaded_asset(b, False)
    if not EAL.does_asset_exist(GD): BT.create(f"{R}/Core", "BP_Guide", unreal.Actor.static_class())
    TG.ensure_vars(GD, [("Stage", "int"), ("bMoving", "bool"), ("Speed", "float")],
                   objs=[("Current", unreal.Actor.static_class()), ("Body", unreal.SkeletalMeshActor.static_class()),
                         ("WalkAnim", unreal.AnimSequence.static_class()), ("IdleAnim", unreal.AnimSequence.static_class())])
    g = lambda n: f"(Variables|Default|Get{n})"
    mesh = f"(Class|SkeletalMeshActor|GetSkeletalMeshComponent :self {g('Body')})"
    hints = "\n".join(f'  (for h{n} (Actor|GetAllActorswithTag :Tag "HintS{n}") (Rendering|SetActorHiddenInGame :self h{n} :bNewHidden (not (== {g("Stage")} {n}))))' for n in range(4))
    starts = "\n".join(f'  (if (== {g("Stage")} {n}) (for s{n} (Actor|GetAllActorswithTag :Tag "GuideStart{n}") (Variables|Default|SetCurrent s{n}) (Transformation|SetActorLocation :NewLocation (Transformation|GetActorLocation :self s{n}) :bTeleport true)))' for n in range(4))
    code = f"""
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

(event EventTick (DeltaSeconds)
  (bind wp (Utilities|Casting|CastToBP_GuideWaypoint :Object {g('Current')})
    (:then
      (bind me (Transformation|GetActorLocation))
      (bind tgt (Transformation|GetActorLocation :self wp))
      (bind pd (Transformation|GetDistanceTo :OtherActor (Game|GetPlayerCharacter 0)))
      (bind wd (Transformation|GetDistanceTo :OtherActor wp))
      (if (and (< pd 700.0) (> wd 15.0))
        (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterptoConstant :Current me :Target tgt :DeltaTime DeltaSeconds :InterpSpeed {g('Speed')}) :bTeleport true)
        (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start (Math|Vector|MakeVector (.x me) (.y me) 0.0) :Target (Math|Vector|MakeVector (.x tgt) (.y tgt) 0.0)) :bTeleportPhysics true)
        (if (not {g('Moving')})
          (Components|Animation|PlayAnimation :self {mesh} :NewAnimToPlay {g('WalkAnim')} :bLooping true)
          (Variables|Default|SetMoving true))
        (else
          (if (<= wd 15.0)
            (Variables|Default|SetCurrent (Class|BPGuideWaypoint|GetNext :self wp)))
          (bind pl (Transformation|GetActorLocation :self (Game|GetPlayerCharacter 0)))
          (if (>= pd 700.0)
            (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start (Math|Vector|MakeVector (.x me) (.y me) 0.0) :Target (Math|Vector|MakeVector (.x pl) (.y pl) 0.0)) :bTeleportPhysics true))
          (if {g('Moving')}
            (Components|Animation|PlayAnimation :self {mesh} :NewAnimToPlay {g('IdleAnim')} :bLooping true)
            (Variables|Default|SetMoving false)))))
    (:CastFailed
      (if {g('Moving')}
        (Components|Animation|PlayAnimation :self {mesh} :NewAnimToPlay {g('IdleAnim')} :bLooping true)
        (Variables|Default|SetMoving false)))))
"""
    r = TG.run(GD, code, events=["Setup"], clear=True)
    b = EAL.load_asset(GD)
    for n in ("Body", "WalkAnim", "IdleAnim", "Speed"): BEL.set_blueprint_variable_instance_editable(b, n, True)
    BEL.compile_blueprint(b); unreal.get_default_object(b.generated_class()).set_editor_property("Speed", 115.0); EAL.save_loaded_asset(b, False)
    return str(r)[:300]

PATHS = {
    0: [(1000, 0, 0), (1700, -60, 0), (2600, 40, 0), (3300, -40, 0), (3420, 130, 0)],
    1: [(3300, -150, 0), (3850, -420, 0), (4000, -550, 0), (4085, -550, 100), (4255, -550, 200), (4425, -550, 300), (5150, -575, 324), (5330, -575, 324)],
    2: [(5300, -575, 324), (5900, -575, 324), (6250, -575, 324), (6330, -470, 324)],
    3: [(6400, 0, 0), (6900, 0, 0), (7600, 0, 0), (8150, 0, 0), (8250, 160, 0)],
}
HINTS = {
    0: ("Stand on the rusty round mark.", "Look at the round window high on the far wall until it lines up.", (3500, 0, 0), 180),
    1: ("Climb the steel beams onto the catwalk (Jump + Shift = Cut Boost).", "From the mark, look at the tall window on the far wall.", (5450, -575, 324), 180),
    2: ("Cut Boost up to the ledge above the catwalk.", "Look through the narrow slit in the far wall.", (6450, -575, 750), 180),
    3: ("This is the unfinished move.", "Step on one of the three marks to choose how it ends.", (8300, 0, 0), 180),
}
def level():
    L.load_level(f"{R}/Maps/M_FactoryHub")
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(("GuideWP_", "Guide_Mara", "Mara_Body", "Hint_S")): E.destroy_actor(a)
    wcls = EAL.load_asset(GW).generated_class()
    for st, pts in PATHS.items():
        prev = None; made = []
        for i, p in enumerate(pts):
            w = E.spawn_actor_from_class(wcls, V(*p), unreal.Rotator()); w.set_actor_label(f"GuideWP_{st}_{i}"); w.set_folder_path(f"Gameplay/Guide/S{st}")
            if i == 0: w.tags = [f"GuideStart{st}"]
            if prev: prev.set_editor_property("Next", w)
            prev = w; made.append(w)
    g = E.spawn_actor_from_class(EAL.load_asset(GD).generated_class(), V(*PATHS[0][0]), unreal.Rotator())
    g.set_actor_label("Guide_Mara"); g.set_folder_path("Gameplay/Guide")
    body = E.spawn_actor_from_class(unreal.SkeletalMeshActor, V(*PATHS[0][0]), unreal.Rotator(roll=0, pitch=0, yaw=-90))
    c = body.skeletal_mesh_component; c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_skeletal_mesh_asset(EAL.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple"))
    ghost = EAL.load_asset(f"{R}/Materials/M_MaraGhost")
    for i in range(c.get_num_materials()): c.set_material(i, ghost)
    c.set_collision_profile_name("NoCollision"); c.set_cast_shadow(False); body.set_actor_enable_collision(False)
    body.set_actor_label("Mara_Body"); body.set_folder_path("Gameplay/Guide")
    body.attach_to_actor(g, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    lt = E.spawn_actor_from_class(unreal.PointLight, V(PATHS[0][0][0], 0, 120), unreal.Rotator())
    lt.point_light_component.set_intensity(1800.0); lt.point_light_component.set_light_color(unreal.LinearColor(1.0, 0.62, 0.3, 1)); lt.point_light_component.set_attenuation_radius(450.0)
    lt.point_light_component.set_mobility(unreal.ComponentMobility.MOVABLE); lt.set_actor_label("Guide_Mara_Glow"); lt.set_folder_path("Gameplay/Guide")
    lt.attach_to_actor(g, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    g.set_editor_property("Body", body)
    g.set_editor_property("WalkAnim", EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd"))
    g.set_editor_property("IdleAnim", EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle"))
    for st, (l1, l2, (x, y, z), yaw) in HINTS.items():
        for j, (txt, dz, size) in enumerate(((l1, 230, 13.0), (l2, 200, 10.0))):
            t = E.spawn_actor_from_class(unreal.TextRenderActor, V(x + 60, y, z + dz), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
            tc = t.text_render; tc.set_text(unreal.Text(txt)); tc.set_world_size(size); tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
            tc.set_text_render_color(unreal.Color(r=255, g=214, b=150, a=255))
            t.tags = [f"HintS{st}"]; t.set_actor_label(f"Hint_S{st}_{j}"); t.set_folder_path("UI/Hints")
    # the patrol searchlight should not read as a person: tint its lamp cold blue
    pl = find("PatrolLight_Lamp")
    if pl: pl.spot_light_component.set_light_color(unreal.LinearColor(0.6, 0.75, 1.0, 1))
    L.save_current_level(); return "ok"

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("material", material); step("bps", blueprints)
    if "bps" in res["ok"]: step("level", level)
    return res
