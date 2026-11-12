import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
LOOKS = {  # map: (exposure bias, gain rgb, saturation, sun mult, fog density, fog color)
 "M_FactoryHub": (-1.6, (0.80, 0.97, 1.05), 0.75, 0.5, 0.06, (0.20, 0.30, 0.36)),
 "M_Cut_WarField": (-1.0, (0.92, 0.95, 1.05), 0.7, 0.8, 0.05, (0.35, 0.38, 0.45)),
 "M_Cut_Cliff": (-0.8, (0.88, 0.95, 1.08), 0.75, 1.0, 0.04, (0.45, 0.5, 0.6)),
 "M_Cut_Dragon": (-0.8, (0.9, 0.95, 1.08), 0.75, 0.8, 0.02, (0.4, 0.45, 0.55)),
 "M_RealRoom": (-0.5, (1.05, 0.98, 0.9), 0.9, 1.0, 0.0, (0.3, 0.3, 0.35)),
}
def pp_settings(pp, bias, gain, sat):
    s = pp.settings
    for k, v in (("override_auto_exposure_method", True), ("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("override_auto_exposure_bias", True), ("auto_exposure_bias", bias),
                 ("override_auto_exposure_apply_physical_camera_exposure", True), ("auto_exposure_apply_physical_camera_exposure", False),
                 ("override_color_gain", True), ("color_gain", unreal.Vector4(gain[0], gain[1], gain[2], 1.0)),
                 ("override_color_saturation", True), ("color_saturation", unreal.Vector4(sat, sat, sat, 1.0)),
                 ("override_vignette_intensity", True), ("vignette_intensity", 0.55), ("override_film_grain_intensity", True), ("film_grain_intensity", 0.15),
                 ("override_bloom_intensity", True), ("bloom_intensity", 0.8)):
        try: s.set_editor_property(k, v)
        except Exception: pass
    pp.settings = s
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    out = {}
    for mp, (bias, gain, sat, sunm, fog, fogc) in LOOKS.items():
        LES.load_level(f"/Game/TUM/Maps/{mp}"); got = []
        for a in EAS.get_all_level_actors():
            if isinstance(a, unreal.PostProcessVolume): pp_settings(a, bias, gain, sat); got.append("pp")
            if isinstance(a, unreal.ExponentialHeightFog):
                fc = a.get_component_by_class(unreal.ExponentialHeightFogComponent)
                if fog > 0: fc.set_fog_density(fog)
                fc.set_fog_inscattering_color(unreal.LinearColor(*fogc, 1)); got.append("fog")
        LES.save_current_level(); out[mp] = got
    LES.load_level("/Game/TUM/Maps/M_FactoryHub"); return out
