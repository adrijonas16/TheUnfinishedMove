import unreal, importlib
import tum_lib as T; importlib.reload(T)
EAS = T.EAS; LES = T.LES
BIAS = {"M_FactoryHub": 0.0, "M_Cut_WarField": 0.3, "M_Cut_Cliff": 0.5, "M_Cut_Dragon": 0.5, "M_RealRoom": 0.5}
EV = 1.0
def pp_fix(bias):
    for a in EAS().get_all_level_actors():
        if isinstance(a, unreal.PostProcessVolume):
            s = a.settings
            for k, v in (("override_auto_exposure_method", True), ("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM),
                         ("override_auto_exposure_min_brightness", True), ("auto_exposure_min_brightness", EV),
                         ("override_auto_exposure_max_brightness", True), ("auto_exposure_max_brightness", EV),
                         ("override_auto_exposure_bias", True), ("auto_exposure_bias", bias),
                         ("override_auto_exposure_apply_physical_camera_exposure", False)):
                try: s.set_editor_property(k, v)
                except Exception: pass
            a.settings = s
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    out = {}
    for mp, b in BIAS.items():
        LES().load_level(f"/Game/TUM/Maps/{mp}"); pp_fix(b)
        if mp == "M_RealRoom":
            for a in EAS().get_all_level_actors():
                if isinstance(a, unreal.PlayerStart): a.set_actor_location(unreal.Vector(-250, 250, 120), False, False); a.set_actor_rotation(unreal.Rotator(0, 0, 135), False)
                if a.get_actor_label() == "AlignAnchor_Factory":
                    a.set_actor_location(unreal.Vector(200, -140, 100), False, False); a.set_editor_property("Radius", 200.0); a.set_editor_property("MinDot", 0.995)
        if mp == "M_FactoryHub":
            for a in EAS().get_all_level_actors():
                if a.get_actor_label() == "PatrolLight":
                    a.set_editor_property("AmpX", 900.0); a.set_editor_property("Speed", 0.35); a.set_editor_property("KillRadius", 170.0); out["patrol"] = "ok"
                if a.get_actor_label() == "CP_Loom2": EAS().destroy_actor(a)
            T.point("CP_Loom2", 1750, 0, 100, "Markers/Checkpoints", ("Checkpoint",))
        LES().save_current_level(); out[mp] = "ok"
    LES().load_level("/Game/TUM/Maps/M_RealRoom"); return out
