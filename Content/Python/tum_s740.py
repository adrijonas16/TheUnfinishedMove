# Factory story beats (stage 0 and 1): she steps out of the dark ("You finally came."), walks off into the unlit bay and is
# gone, then calls from the steel platform ("I'm here." / "Come up." / "How?") and a white flash cuts to the dragon. After the
# dragon she waits at a locked catwalk gate ("It won't open without the seal.") and a flash cuts to the war. The old
# stand-on-the-mark-and-line-up anchors for those two cuts are switched off.
import unreal, importlib, traceback
import tum_graph as TG; importlib.reload(TG)
import tum_s666 as Q
import tum_s612 as T612
import tum_fac as K; importlib.reload(K)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; E = K.E; V = unreal.Vector; L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
R = "/Game/TUM"; SL = f"{R}/Core/BP_SayLine"; GW = f"{R}/Core/BP_GuideWaypoint"; TAGB = "BEAT2"
GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
WHITE = "(Utilities|Struct|MakeLinearColor :R 1.0 :G 1.0 :B 1.0 :A 1.0)"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
g = lambda n: f"(Variables|Default|Get{n})"
def code():
    return f"""
(event EventBeginPlay
  (Variables|Default|SetStage 0.0)
  (bind gi {GP}
    (:then
      (if (Class|BPGameProgress|GetDragonDone :self gi)
        (Variables|Default|SetStage 1.0))
      (if (Class|BPGameProgress|GetWarDone :self gi)
        (Variables|Default|SetStage 2.0))
      (if (Class|BPGameProgress|GetCliffDone :self gi)
        (Variables|Default|SetStage 3.0))
      (CallFunction|Arm))
    (:CastFailed (CallFunction|Arm))))

(event Custom|Arm
  (Actor|Tick|SetActorTickEnabled :bEnabled (and (> {g('Stage')} (- {g('MinStage')} 0.5)) (< {g('Stage')} (+ {g('MaxStage')} 0.5)))))

(event EventTick (DeltaSeconds)
  (bind dist (Transformation|GetDistanceTo :OtherActor (Game|GetPlayerCharacter 0)))
  (if (and (not {g('Used')}) (and (> dist 1.0) (< dist {g('Radius')})))
    (Variables|Default|SetUsed true)
    (CallFunction|Fire)))

(event Custom|Fire
  (Utilities|FlowControl|Delay {g('StartDelay')})
  (for a (Actor|GetAllActorswithTag :Tag {g('ShowTag')})
    (Rendering|SetActorHiddenInGame :self a :bNewHidden false))
  (for b (Actor|GetAllActorswithTag :Tag {g('HideTag')})
    (Rendering|SetActorHiddenInGame :self b :bNewHidden true)
    (Collision|SetActorEnableCollision :self b :bNewActorEnableCollision false))
  (if {g('OpenMap')}
    (Input|DisableInput :self (Game|GetPlayerCharacter 0) :PlayerController (Game|GetPlayerController 0))
    (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager 0) :FromAlpha 0.0 :ToAlpha 1.0 :Duration 0.22 :Color {WHITE} :bHoldWhenFinished true)
    (Utilities|FlowControl|Delay 0.5)
    (Game|OpenLevel(byName) :LevelName {g('TargetMap')})
    (else
      (if {g('Temporary')}
        (Utilities|FlowControl|Delay {g('Hold')})
        (for c (Actor|GetAllActorswithTag :Tag {g('ShowTag')})
          (Rendering|SetActorHiddenInGame :self c :bNewHidden true))))))
"""
EDIT = ["Radius", "ShowTag", "HideTag", "MinStage", "MaxStage", "StartDelay", "Hold", "bTemporary", "bOpenMap", "TargetMap"]
def blueprint():
    if not EAL.does_asset_exist(SL): BT.create(f"{R}/Core", "BP_SayLine", unreal.Actor.static_class())
    TG.ensure_vars(SL, [("Radius", "float"), ("ShowTag", "name"), ("HideTag", "name"), ("MinStage", "float"), ("MaxStage", "float"), ("Stage", "float"), ("StartDelay", "float"), ("Hold", "float"),
                        ("bTemporary", "bool"), ("bOpenMap", "bool"), ("TargetMap", "name"), ("bUsed", "bool")])
    bp = EAL.load_asset(SL)
    for ev in ("Arm", "Fire"):
        try: BT.add_event(bp, ev)
        except Exception: pass
    graph = BEL.find_event_graph(bp); c = T612._resolve(SL, code()); miss = TG.check_ids(graph, c)
    miss = [m for m in miss if not m.startswith("CallFunction|")]
    if miss or TG.balance(c): return {"aborted": miss, "balance": TG.balance(c)}
    r = Q.patched(lambda: str(TG.run(SL, c, events=["Arm", "Fire"], clear=True))[:200])
    bp = EAL.load_asset(SL)
    for n in EDIT: BEL.set_blueprint_variable_instance_editable(bp, n, True)
    BEL.compile_blueprint(bp); cdo = unreal.get_default_object(bp.generated_class())
    for k, v in (("Radius", 300.0), ("Hold", 3.5), ("MaxStage", 9.0)): cdo.set_editor_property(k, v)
    EAL.save_loaded_asset(bp, False); return r
PATHS = {0: [(1350, -520, 0), (1100, -120, 0), (2300, 0, 0), (3250, -60, 0), (3750, -330, 0)],
         1: [(5300, -575, 324), (5620, -575, 324)],
         2: [(5650, -575, 324), (6250, -575, 750), (6400, -575, 750), (6480, -470, 750)]}
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a
def say(label, pos, radius, show="None", hide="None", stage=(0, 0), delay=0.0, hold=0.0, map_=None):
    a = E.spawn_actor_from_class(EAL.load_asset(SL).generated_class(), V(*pos), unreal.Rotator())
    for k, v in (("Radius", float(radius)), ("ShowTag", show), ("HideTag", hide), ("MinStage", float(stage[0])), ("MaxStage", float(stage[1])), ("StartDelay", float(delay)),
                 ("Hold", float(hold)), ("bTemporary", hold > 0), ("bOpenMap", bool(map_)), ("TargetMap", map_ or "None")): a.set_editor_property(k, v)
    a.set_actor_label(label); a.set_folder_path("Gameplay/Beats"); a.tags = [unreal.Name(TAGB)]; return a
def line(label, pos, text, size, color, tag, yaw=180.0):
    a = E.spawn_actor_from_class(unreal.TextRenderActor, V(*pos), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    t = a.text_render; t.set_text(unreal.Text(text)); t.set_world_size(size); t.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    t.set_text_render_color(unreal.Color(r=int(color[0] * 255), g=int(color[1] * 255), b=int(color[2] * 255), a=255))
    a.set_actor_hidden_in_game(True); a.set_actor_label(label); a.set_folder_path("Gameplay/Beats"); a.tags = [unreal.Name(TAGB), unreal.Name(tag)]; return a
def level():
    out = {}
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label()
        if unreal.Name(TAGB) in a.tags or lab.startswith(("GuideWP_0_", "GuideWP_1_", "GuideWP_2_", "Hint_S0_", "Hint_S1_", "Hint_Follow_")) or (unreal.Name(K.TAG) in a.tags and str(a.get_folder_path()).startswith("Art/Fac2/Door")):
            E.destroy_actor(a)
    wcls = EAL.load_asset(GW).generated_class()
    for st, pts in PATHS.items():
        prev = None
        for i, p in enumerate(pts):
            w = E.spawn_actor_from_class(wcls, V(*p), unreal.Rotator()); w.set_actor_label(f"GuideWP_{st}_{i}"); w.set_folder_path(f"Gameplay/Guide/S{st}")
            if i == 0: w.tags = [f"GuideStart{st}"]
            if prev: prev.set_editor_property("Next", w)
            prev = w
    guide = find("Guide_Mara"); body = find("Mara_Body"); glow = find("Guide_Mara_Glow")
    for a in (body, glow):
        if a and unreal.Name("MaraWalk") not in a.tags: a.tags = list(a.tags) + [unreal.Name("MaraWalk")]
    # she, standing on the platform
    bc = body.skeletal_mesh_component; off = body.get_actor_rotation().yaw - guide.get_actor_rotation().yaw
    up = E.spawn_actor_from_class(unreal.SkeletalMeshActor, V(4440, -550, 300), unreal.Rotator(roll=0, pitch=0, yaw=180 + off + 20))
    uc = up.skeletal_mesh_component; uc.set_mobility(unreal.ComponentMobility.MOVABLE); uc.set_skeletal_mesh_asset(bc.get_skeletal_mesh_asset())
    for i in range(bc.get_num_materials()): uc.set_material(i, bc.get_material(i))
    uc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE); d = unreal.SingleAnimationPlayData()
    d.set_editor_property("anim_to_play", guide.get_editor_property("IdleAnim")); d.set_editor_property("saved_looping", True); d.set_editor_property("saved_playing", True); uc.set_editor_property("animation_data", d)
    uc.set_collision_profile_name("NoCollision"); uc.set_cast_shadow(False); up.set_actor_enable_collision(False); up.set_actor_scale3d(body.get_actor_scale3d())
    up.set_actor_hidden_in_game(True); up.set_actor_label("Mara_Up"); up.set_folder_path("Gameplay/Beats"); up.tags = [unreal.Name(TAGB), unreal.Name("MaraUp")]
    lt = E.spawn_actor_from_class(unreal.PointLight, V(4440, -550, 420), unreal.Rotator()); pc = lt.point_light_component
    pc.set_intensity(1500.0); pc.set_light_color(unreal.LinearColor(1.0, 0.62, 0.3, 1)); pc.set_attenuation_radius(420.0); pc.set_mobility(unreal.ComponentMobility.MOVABLE)
    lt.set_actor_hidden_in_game(True); lt.set_actor_label("Mara_Up_Glow"); lt.set_folder_path("Gameplay/Beats"); lt.tags = [unreal.Name(TAGB), unreal.Name("MaraUp")]
    amber, white = (1.0, 0.84, 0.59), (0.82, 0.88, 1.0)
    line("L_Finally", (1100, -120, 222), "You finally came.", 20.0, amber, "L_Finally")
    line("L_ImHere", (4440, -550, 535), "I'm here.", 44.0, amber, "L_ImHere", yaw=165.0)
    line("L_ComeUp", (4440, -550, 535), "Come up.", 44.0, amber, "L_ComeUp", yaw=165.0)
    line("L_How", (4300, -470, 215), "How?", 24.0, white, "L_How", yaw=160.0)
    line("L_Seal", (5640, -575, 548), "It won't open without the seal.", 18.0, amber, "L_Seal")
    say("Say_Finally", (1100, -120, 100), 520, show="L_Finally", hold=4.5)
    say("Say_Vanish", (3750, -330, 100), 430, show="MaraUp", hide="MaraWalk")
    say("Say_ImHere", (3750, -330, 100), 430, show="L_ImHere", delay=0.6, hold=3.2)
    say("Say_ComeUp", (4150, -480, 100), 340, show="L_ComeUp", hold=2.6)
    say("Say_How", (4150, -480, 100), 340, show="L_How", delay=2.4, hold=1.9)
    say("Say_Dragon", (4150, -480, 100), 340, delay=4.5, map_="M_Cut_Dragon")
    say("Say_Seal", (5560, -575, 424), 240, show="L_Seal", stage=(1, 1), hold=3.2)
    say("Say_War", (5560, -575, 424), 240, stage=(1, 1), delay=3.4, map_="M_Cut_WarField")
    say("Say_DoorOpen", (5500, -575, 428), 100000, hide="WarDoor", stage=(2, 9))
    # the locked gate across the catwalk
    st, rl = K.asset(f"{K.MS}/MI_W_SteelDark"), K.asset(f"{K.MS}/MI_W_RailPaint"); D = "Art/Fac2/Door"; made = []
    for y in (-697, -453): made.append(K.box(f"Gate_post{y}", 5682, 5694, y - 6, y + 6, 324, 570, st, D))
    made.append(K.box("Gate_lintel", 5682, 5694, -703, -447, 558, 572, st, D))
    for i in range(11): y = -690 + i * 23; made.append(K.box(f"Gate_bar{i}", 5686, 5690, y - 1.5, y + 1.5, 330, 556, rl, D, shadow=False))
    for z in (345, 450, 545): made.append(K.box(f"Gate_cross{z}", 5685, 5691, -692, -458, z - 3, z + 3, rl, D, shadow=False))
    made.append(K.box("Gate_lock", 5678, 5686, -590, -560, 436, 464, st, D, shadow=False))
    w = K.box("Gate_block", 5680, 5696, -700, -450, 324, 600, K.asset(f"{K.MS}/M_Invisible"), D, collide=True, shadow=False); w.set_actor_hidden_in_game(True); made.append(w)
    for a in made: a.tags = list(a.tags) + [unreal.Name("WarDoor")]
    # old line-up anchors for dragon and war: off, with their props
    for n in ("AlignAnchor_Dragon", "AlignAnchor_War"):
        a = find(n)
        if a: a.set_editor_property("Radius", 0.0)
    hid = 0
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab in ("Skin_Anchor_Dragon_Lamp", "Skin_Anchor_Dragon_Spot", "Skin_Lamp_Hang", "Skin_Anchor_War_Spot", "Skin_Anchor_Dragon_RoundWindow", "Skin_Anchor_War_Window", "Skin_Anchor_War_Banner"):
            a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True); hid += 1
        if lab in ("Goal_Glow_0", "Goal_Glow_1"):
            c = a.get_component_by_class(unreal.LightComponent); c.set_visibility(False); c.set_editor_property("visible", False); hid += 1
    out["hidden"] = hid
    hud = find("ObjectiveHUD")
    for k, v in (("ObjText0", "Follow her"), ("Hint0", "She walked off into the dark. Find where she went."),
                 ("ObjText1", "Follow her along the catwalk"), ("Hint1", "Cut Boost (Jump + Shift) carries you across the gap."),
                 ("ObjText2", "Climb to the high ledge")):
        try: hud.set_editor_property(k, v)
        except Exception as ex: out.setdefault("hud_err", []).append(repr(ex)[:120])
    return out
def run(bp=True):
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_FactoryHub")
    if bp: step("blueprint", blueprint)
    if not res["err"] and not (isinstance(res.get("blueprint"), dict) and res["blueprint"].get("aborted") is not None and (res["blueprint"]["aborted"] or res["blueprint"]["balance"])):
        step("level", level)
        if not res["err"]: L.save_current_level()
    return res
