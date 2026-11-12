import unreal, importlib
import tum_lib as T; importlib.reload(T)
import tum_shot as SH; importlib.reload(SH)
EAL = unreal.EditorAssetLibrary
def hidebox(w): w.set_actor_hidden_in_game(True); w.static_mesh_component.set_visibility(False)
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    T.LES().load_level("/Game/TUM/Maps/M_FactoryHub")
    for a in T.EAS().get_all_level_actors():
        if unreal.Name("Exterior") in a.tags or a.get_actor_label() == "Wall_Start": T.EAS().destroy_actor(a)
    fac = [a for a in T.EAS().get_all_level_actors() if a.get_actor_label() == "Ext_Facade"][0]
    m = EAL.load_asset("/Game/TUM/Environment/Facade/FBX_1_mln_2x16K_N"); bb = m.get_bounding_box()
    cx, cy = (bb.min.x + bb.max.x) / 2, (bb.min.y + bb.max.y) / 2
    fac.set_actor_rotation(unreal.Rotator(0, 0, 180), False)
    fac.set_actor_location(unreal.Vector(-762 + cx, cy, -bb.min.z), False, False)
    E = ("Exterior",); F = "Exterior"
    asph = "/Game/TUM/Materials/Surfaces/MI_Asphalt031"; conc = "/Game/TUM/Materials/Surfaces/MI_Concrete044A"
    T.box("Ext_Ground", -7000, -1150, -5000, 5000, -20, 0, asph, F, E)
    T.box("Ext_Passage_Floor", -1200, -300, -260, 260, -20, 0, conc, F, E)
    for s, y0, y1 in (("S", -300, -260), ("N", 260, 300)): T.box(f"Ext_Passage_Wall{s}", -1200, -300, y0, y1, 0, 600, conc, F, E)
    T.box("Ext_Passage_Roof", -1200, -300, -300, 300, 600, 640, conc, F, E)
    for s, y0, y1 in (("S", -800, -260), ("N", 260, 800)): T.box(f"Wall_Start_{s}", -340, -300, y0, y1, 0, 1100, conc, "Graybox/Shell", E)
    T.box("Wall_Start_Top", -340, -300, -260, 260, 600, 1100, conc, "Graybox/Shell", E)
    for s, y0, y1 in (("S", -4300, -260), ("N", 260, 4300)): hidebox(T.box(f"Ext_FacadeBlock_{s}", -1220, -1180, y0, y1, 0, 2400, conc, F, E))
    for s, y0, y1 in (("S", -5040, -5000), ("N", 5000, 5040)): hidebox(T.box(f"Ext_Bound_{s}", -7000, -1150, y0, y1, 0, 2000, conc, F, E))
    hidebox(T.box("Ext_Bound_W", -7040, -7000, -5000, 5000, 0, 2000, conc, F, E))
    for i, (x, y) in enumerate(((-2200, -900), (-2200, 900), (-4200, -1400), (-4200, 1400))):
        l = T.light(f"Ext_Sodium_{i}", x, y, 650, (1.0, 0.72, 0.35), 9000.0, 1800.0, F); l.tags = list(l.tags) + [unreal.Name("Exterior")]
    l = T.light("Ext_GateLight", -1300, 0, 520, (0.75, 0.85, 1.0), 6000.0, 900.0, F); l.tags = list(l.tags) + [unreal.Name("Exterior")]
    for a in T.EAS().get_all_level_actors():
        if isinstance(a, unreal.PlayerStart): a.set_actor_location(unreal.Vector(-5200, 0, 120), False, False); a.set_actor_rotation(unreal.Rotator(0, 0, 0), False)
    T.point("CP_Outside", -5000, 0, 100, "Markers/Checkpoints", ("Checkpoint", "Exterior"))
    T.LES().save_current_level()
    return SH.shots("M_FactoryHub", {"ext_view": ((-5600, 0, 250), (2, 0), 85), "ext_wide": ((-6800, -2500, 1500), (-8, 20), 85)})
