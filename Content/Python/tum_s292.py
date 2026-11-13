# On-screen objective line (camera-attached text) on every map + title card at game start
import unreal, importlib, traceback, math
import tum_graph as TG; importlib.reload(TG)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; HUD = f"{R}/Core/BP_ObjectiveHUD"; GPB = f"{R}/Core/BP_GameProgress"
GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]

def hud_bp():
    if not EAL.does_asset_exist(HUD): BT.create(f"{R}/Core", "BP_ObjectiveHUD", unreal.Actor.static_class())
    TG.ensure_vars(HUD, [("Stage", "int"), ("bFactory", "bool"), ("Dist", "float"), ("Drop", "float")])
    g = lambda n: f"(Variables|Default|Get{n})"
    hints = "\n".join(f'  (for h{n} (Actor|GetAllActorswithTag :Tag "HUDS{n}") (Rendering|SetActorHiddenInGame :self h{n} :bNewHidden (not (== {g("Stage")} {n}))))' for n in range(4))
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
{hints})

(event EventTick (DeltaSeconds)
  (bind cm (Game|GetPlayerCameraManager 0))
  (bind cl (Camera|GetCameraLocation :self cm))
  (bind cr (Camera|GetCameraRotation :self cm))
  (bind f (Math|Vector|GetForwardVector :InRot cr))
  (bind u (Math|Vector|GetUpVector :InRot cr))
  (bind p (Math|Vector|MakeVector (+ (.x cl) (+ (* (.x f) {g('Dist')}) (* (.x u) {g('Drop')}))) (+ (.y cl) (+ (* (.y f) {g('Dist')}) (* (.y u) {g('Drop')}))) (+ (.z cl) (+ (* (.z f) {g('Dist')}) (* (.z u) {g('Drop')})))))
  (for t (Actor|GetAllActorswithTag :Tag "HUDText")
    (Transformation|SetActorLocationAndRotation :self t :NewLocation p :NewRotation (Math|Rotator|FindLookatRotation :Start p :Target cl) :bTeleport true)))
"""
    r = TG.run(HUD, code, events=["Setup"], clear=True)
    b = EAL.load_asset(HUD); BEL.set_blueprint_variable_instance_editable(b, "bFactory", True); BEL.compile_blueprint(b)
    cdo = unreal.get_default_object(b.generated_class()); cdo.set_editor_property("Dist", 70.0); cdo.set_editor_property("Drop", -27.0)
    EAL.save_loaded_asset(b, False)
    return str(r)[:300]

TEXT = {
    "M_RealRoom": ["Night. Rain. Sit at your desk  (walk to the chair, press E)"],
    "M_FactoryHub": ["Follow the amber figure.  Stand on the round mark and LOOK at the round window to cut into the memory.",
                     "Follow her to the steel beams.  Climb to the catwalk (SPACE, then SHIFT = Cut Boost)  and LOOK at the tall window.",
                     "Cut Boost up to the high ledge  and LOOK through the narrow slit in the far wall.",
                     "The last move.  Step on one of the three marks at the chessboard, then take the way out it opens."],
    "M_Cut_Dragon": ["Fly with the dragon.  WASD + mouse to steer around the rocks.  SHIFT = Cut Boost through every stone arch."],
    "M_Cut_WarField": ["Cross the battle.  Don't let the knights touch you.  Reach the shrine, cut the rope, take the silver seal."],
    "M_Cut_Cliff": ["The path is hidden.  Stand still and LOOK at the far stone arch to reveal it, then cross before it fades."],
}
def place_all():
    out = {}
    for mp, lines in TEXT.items():
        L.load_level(f"{R}/Maps/{mp}")
        for a in list(E.get_all_level_actors()):
            if a.get_actor_label().startswith(("HUD_", "ObjectiveHUD")): E.destroy_actor(a)
        h = E.spawn_actor_from_class(EAL.load_asset(HUD).generated_class(), V(0, 0, 0), unreal.Rotator())
        h.set_actor_label("ObjectiveHUD"); h.set_folder_path("UI"); h.set_editor_property("bFactory", mp == "M_FactoryHub")
        for i, line in enumerate(lines):
            t = E.spawn_actor_from_class(unreal.TextRenderActor, V(0, 0, -5000), unreal.Rotator())
            t.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            tc = t.text_render; tc.set_text(unreal.Text(line)); tc.set_world_size(1.55)
            tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER); tc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
            tc.set_text_render_color(unreal.Color(r=255, g=226, b=180, a=255)); tc.set_cast_shadow(False)
            t.tags = ["HUDText", f"HUDS{i}"]; t.set_actor_label(f"HUD_{i}"); t.set_folder_path("UI")
        L.save_current_level(); out[mp] = len(lines)
    return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("hud", hud_bp)
    if "hud" in res["ok"]: step("place", place_all)
    return res
