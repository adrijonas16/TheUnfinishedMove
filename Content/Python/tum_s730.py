# Factory as an abandoned factory: the stretched x8 warehouse shell and oversized pipes/planks go away; the hall is rebuilt on the
# real collision walls with brick, steel columns and trusses, tall window bays lit only from the street side, a wet concrete
# floor, steel catwalks with railings and real stairs. Gameplay boxes, anchors, guide path and spawn points are untouched.
import unreal, importlib, math, random, traceback
import tum_fac as K; importlib.reload(K)
EAL = unreal.EditorAssetLibrary; E = K.E; V = unreal.Vector; L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
MS = K.MS; F = "Art/Fac2"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
M = {}
def materials():
    M["brick"] = K.asset(f"{MS}/MI_Bricks059"); M["conc"] = K.asset(f"{MS}/MI_W_WallPainted"); M["roof"] = K.mi("RoofSheet", "MetalCorroded", folder="Ind_Sheet_Metal_Corroded_26", tile=320.0, rough=0.85, metal=0.3, tint=(0.22, 0.22, 0.24))
    M["steel"] = K.mi("SteelDark", "MetalCorroded", folder="Ind_Sheet_Metal_Corroded_27", tile=220.0, rough=0.75, metal=0.7, tint=(0.42, 0.42, 0.45))
    M["rail"] = K.mi("RailPaint", "MetalCorroded", folder="Ind_Sheet_Metal_Scratched_02", tile=160.0, rough=0.6, metal=0.6, tint=(0.55, 0.5, 0.3))
    M["grate"] = K.mi("Grate", "MetalCorroded", folder="Ind_Sheet_Metal_Scratched_02", tile=140.0, rough=0.6, metal=0.7, tint=(0.4, 0.42, 0.45))
    M["floor"] = K.mi("FloorWet", "FloorDirty", folder="Ind_Floor_Concrete_16", tile=520.0, rough=0.32, tint=(0.6, 0.63, 0.66))
    M["rust"] = K.asset(f"{MS}/MI_W_MetalCorroded"); M["black"] = K.asset(f"{MS}/M_BlackAluminum"); M["inv"] = K.asset(f"{MS}/M_Invisible")
    M["glass"] = K.glow("M_FacWindowStreet", (0.5, 0.68, 1.0), 1.1); M["glass_warm"] = K.glow("M_FacWindowSodium", (1.0, 0.62, 0.3), 1.0); M["glass_dim"] = K.glow("M_FacWindowDim", (0.22, 0.3, 0.45), 0.25)
    return sorted(M.keys())
def cleanup():
    out = {"hidden": 0, "destroyed": 0, "lights_off": 0}
    out["cleared"] = K.clear()
    for a in list(E.get_all_level_actors()):
        f = str(a.get_folder_path()); lab = a.get_actor_label()
        if f.startswith("Art/Factory/Stacks") or (f.startswith("Art/Factory/GrayboxSkins") and lab.startswith(("Skin_Entry_HighCatwalk", "Skin_Catwalk_Raised", "Skin_Exit_BlockExit", "Skin_Cliff_Ledge"))):
            E.destroy_actor(a); out["destroyed"] += 1; continue
        old = f.startswith(("Art/Interior", "Art/Factory/Pipes", "Art/Factory/Chains", "Art/Factory/Cables", "Art/Factory/Lights", "Art/Factory/Nave")) or lab.startswith(("CP_F0_Pole", "CP_F1_Pole", "CP_F2_Pole", "CP_F3_Pole", "CP_F0_Flag", "CP_F1_Flag", "CP_F2_Flag", "CP_F3_Flag", "Spine_Lamp_", "Cover_Crane_"))
        if old and not isinstance(a, unreal.Light):
            a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True); a.set_actor_enable_collision(False); out["hidden"] += 1
        if isinstance(a, unreal.Light) and (f.startswith("Lights/Windows") or lab.startswith("Spine_Light_")):
            c = a.get_component_by_class(unreal.LightComponent); c.set_visibility(False); c.set_editor_property("visible", False); out["lights_off"] += 1
    return out
def rematerial():
    """Megascans MIs on scaled cubes stretch with the cube: swap them for the world-aligned versions."""
    n = {"floor": 0, "wall": 0, "metal": 0}
    for a in E.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor): continue
        c = a.static_mesh_component; sm = c.static_mesh
        if not sm or sm.get_name() not in ("Cube", "Cylinder", "Plane"): continue
        m = c.get_material(0); nm = m.get_name() if m else ""
        if nm.startswith("MI_Ind_Unf_Floor") or nm == "MI_W_FloorDirty": c.set_material(0, M["floor"]); n["floor"] += 1
        elif nm.startswith(("MI_Ind_Unf_Wall", "MI_Ind_Wall")): c.set_material(0, M["conc"]); n["wall"] += 1
        elif nm.startswith("MI_Ind_Sheet_Metal"): c.set_material(0, M["rust"]); n["metal"] += 1
    return n
X0, X1, YH, ZR = -300.0, 7500.0, 800.0, 1100.0; NB = 9; BW = (X1 - X0) / NB
def shell():
    random.seed(5)
    # roofs
    K.box("Roof_Main", X0 - 40, X1, -YH - 40, YH + 40, ZR, ZR + 30, M["roof"], F + "/Shell"); K.box("Roof_Nave", X1, 9840, -1140, 1140, 1400, 1430, M["roof"], F + "/Shell")
    K.box("Nave_Gable", X1 - 20, X1 + 20, -1140, 1140, ZR, 1400, M["brick"], F + "/Shell")
    for s in (-1, 1): K.box(f"Nave_Return_{s}", X1 - 20, X1 + 20, s * YH, s * 1140, 0, ZR, M["brick"], F + "/Shell")
    for i in range(NB):
        a, b = X0 + i * BW, X0 + (i + 1) * BW
        # north (street side): real openings so the street light falls in through the mullions
        K.box(f"WN_dado_{i}", a, b, YH, YH + 40, 0, 360, M["brick"], F + "/Shell"); K.box(f"WN_lintel_{i}", a, b, YH, YH + 40, 920, ZR, M["conc"], F + "/Shell")
        K.box(f"WN_pierA_{i}", a, a + 130, YH, YH + 40, 360, 920, M["brick"], F + "/Shell"); K.box(f"WN_pierB_{i}", b - 130, b, YH, YH + 40, 360, 920, M["brick"], F + "/Shell")
        K.box(f"WN_sill_{i}", a + 120, b - 120, YH - 14, YH + 40, 350, 362, M["conc"], F + "/Shell", shadow=False)
        br = [(random.randrange(4), random.randrange(5)) for _ in range(random.choice((0, 1, 2)))]
        K.window(f"WinN_{i}", a + 130, b - 130, YH + 22, 362, 920, M["glass_warm"] if i in (3, 6) else M["glass"], M["steel"], F + "/Windows", broken=br, dark=M["black"])
        # south (dark side): solid wall, dead windows
        K.box(f"WS_wall_{i}", a, b, -YH - 40, -YH, 0, ZR, M["brick"], F + "/Shell")
        K.box(f"WS_sill_{i}", a + 120, b - 120, -YH - 2, -YH + 12, 350, 362, M["conc"], F + "/Shell", shadow=False)
        br = [(random.randrange(4), random.randrange(5)) for _ in range(random.choice((2, 3, 5)))]
        K.window(f"WinS_{i}", a + 130, b - 130, -YH + 3, 362, 920, M["glass_dim"], M["steel"], F + "/Windows", broken=br, dark=M["black"])
    # nave: tall dead windows on both long walls
    for j, x in enumerate((7780, 8480, 9180)):
        for s in (-1, 1):
            K.window(f"WinNave_{j}_{s}", x, x + 520, s * 1097, 420, 1180, M["glass"] if s > 0 else M["glass_dim"], M["steel"], F + "/Windows", cols=4, rows=6, broken=[(1, 2), (3, 4)] if s < 0 else [(2, 5)], dark=M["black"])
    return "ok"
def structure():
    for k in range(1, NB):
        x = X0 + k * BW
        for s in (-1, 1): K.hcol(f"Col_{k}_{s}", x, s * (YH - 26), 0, 945, M["steel"], F + "/Steel")
        K.truss(f"Truss_{k}", x, -YH + 8, YH - 8, 945, 1085, M["steel"], F + "/Steel")
    for j, y in enumerate((-560, 0, 560)): K.bar(f"Purlin_{j}", (X0, y, 1092), (X1, y, 1092), 10, 12, M["steel"], F + "/Steel", shadow=False)
    # crane rails along both walls + the dead gantry crane
    for s in (-1, 1):
        K.bar(f"CraneRail_{s}", (X0 + 300, s * (YH - 60), 700), (7000, s * (YH - 60), 700), 16, 26, M["rust"], F + "/Steel")
        for k in range(1, NB): x = X0 + k * BW; K.box(f"Bracket_{k}_{s}", x - 8, x + 8, s * (YH - 72) if s > 0 else s * (YH - 44), s * (YH - 44) if s > 0 else s * (YH - 72), 672, 688, M["rust"], F + "/Steel", shadow=False)
    gx = 2300.0
    for dx in (-45, 45): K.bar(f"Gantry_{dx}", (gx + dx, -YH + 60, 730), (gx + dx, YH - 60, 730), 22, 46, M["rust"], F + "/Steel")
    K.box("Gantry_Trolley", gx - 60, gx + 60, 150, 290, 700, 770, M["steel"], F + "/Steel"); K.bar("Gantry_Cable", (gx, 220, 700), (gx, 220, 470), 3, 3, M["black"], F + "/Steel", shadow=False)
    K.box("Gantry_Hook", gx - 14, gx + 14, 206, 234, 430, 470, M["rust"], F + "/Steel", shadow=False)
    for j, x in enumerate((7700, 8300, 9000, 9600)):
        for s in (-1, 1): K.hcol(f"NCol_{j}_{s}", x, s * 1072, 0, 1250, M["steel"], F + "/Steel", size=40)
        K.truss(f"NTruss_{j}", x, -1090, 1090, 1250, 1395, M["steel"], F + "/Steel", panel=300)
    return "ok"
def lights():
    n = 0
    for i in (0, 2, 3, 5, 6, 8):
        xc = X0 + (i + 0.5) * BW; warm = i in (3, 6)
        l = E.spawn_actor_from_class(unreal.SpotLight, V(xc + 120, 1500, 1300), unreal.Rotator(roll=0, pitch=-37.5, yaw=-97.0))
        c = l.get_component_by_class(unreal.SpotLightComponent); c.set_mobility(unreal.ComponentMobility.MOVABLE)
        c.set_intensity(13000.0 if not warm else 10000.0); c.set_light_color(unreal.LinearColor(1.0, 0.66, 0.36, 1) if warm else unreal.LinearColor(0.6, 0.76, 1.0, 1))
        c.set_editor_property("attenuation_radius", 3400.0); c.set_outer_cone_angle(27.0); c.set_inner_cone_angle(19.0)
        c.set_editor_property("volumetric_scattering_intensity", 1.6); c.set_cast_shadows(True)
        l.set_actor_label(f"StreetLight_{i}"); l.set_folder_path(F + "/Lights"); l.tags = [unreal.Name(K.TAG)]; n += 1
    for j, x in enumerate((8040, 9440)):
        l = E.spawn_actor_from_class(unreal.SpotLight, V(x, 1040, 900), unreal.Rotator(roll=0, pitch=-38, yaw=-90))
        c = l.get_component_by_class(unreal.SpotLightComponent); c.set_mobility(unreal.ComponentMobility.MOVABLE); c.set_intensity(7000.0); c.set_light_color(unreal.LinearColor(0.6, 0.76, 1.0, 1))
        c.set_editor_property("attenuation_radius", 3000.0); c.set_outer_cone_angle(30.0); c.set_inner_cone_angle(20.0); c.set_editor_property("volumetric_scattering_intensity", 1.4); c.set_cast_shadows(False)
        l.set_actor_label(f"NaveLight_{j}"); l.set_folder_path(F + "/Lights"); l.tags = [unreal.Name(K.TAG)]; n += 1
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.ExponentialHeightFog):
            c = a.get_editor_property("component")
            for k, v in (("enable_volumetric_fog", True), ("volumetric_fog", True), ("volumetric_fog_scattering_distribution", 0.7), ("volumetric_fog_extinction_scale", 1.6), ("fog_density", 0.011)):
                try: c.set_editor_property(k, v)
                except Exception: pass
        if isinstance(a, unreal.SkyLight): a.get_component_by_class(unreal.SkyLightComponent).set_intensity(0.1)
    return n
def rods(name, pts, z0, z1):
    for i, (x, y) in enumerate(pts): K.bar(f"{name}_rod{i}", (x, y, z0), (x, y, z1), 3, 3, M["steel"], F + "/Walk", shadow=False)
def legs(name, pts, z):
    for i, (x, y) in enumerate(pts): K.box(f"{name}_leg{i}", x - 7, x + 7, y - 7, y + 7, 0, z, M["steel"], F + "/Walk")
def walkways():
    W = F + "/Walk"; g, e, r = M["grate"], M["steel"], M["rail"]
    # entry high catwalk (the first place she is seen) and the stair that broke off under it
    K.deck("Entry", 300, 1500, 350, 600, 544, g, e, W); legs("Entry", [(x, y) for x in (330, 900, 1470) for y in (362, 588)], 518)
    K.railing("Entry_RailS", [(300, 352, 544), (1500, 352, 544)], r, W, collide_wall=False); K.railing("Entry_RailN", [(300, 598, 544), (1500, 598, 544)], r, W, collide_wall=False)
    K.railing("Entry_RailE", [(1498, 352, 544), (1498, 598, 544)], r, W, collide_wall=False)
    K.box("Entry_Plinth", 1000, 1300, 350, 600, 0, 260, M["conc"], W)
    K.stairs("Entry_StairStub", 1300, 1090, 380, 570, 400, 544, g, e, W)
    # the platform she calls from, and the stair that only exists once the dragon memory is done
    K.deck("Tower", 4340, 4510, -650, -450, 300, g, e, W); legs("Tower", [(x, y) for x in (4350, 4500) for y in (-640, -460)], 274)
    K.railing("Tower_RailS", [(4340, -648, 300), (4510, -648, 300)], r, W, collide_wall=False); K.railing("Tower_RailN", [(4340, -452, 300), (4510, -452, 300)], r, W, collide_wall=False)
    K.railing("Tower_RailE_a", [(4508, -648, 300), (4508, -615, 300)], r, W, collide_wall=False); K.railing("Tower_RailE_b", [(4508, -485, 300), (4508, -452, 300)], r, W, collide_wall=False)
    before = set(a.get_path_name() for a in E.get_all_level_actors())
    K.stairs("Tower_Stair", 4000, 4340, -640, -460, 0, 300, g, e, W)
    K.railing("Tower_StairRail", [(4000, -462, 0), (4340, -462, 300)], r, W, collide_wall=False)
    for a in E.get_all_level_actors():
        if a.get_path_name() not in before: a.tags = list(a.tags) + [unreal.Name("DragonLift")]; a.set_actor_hidden_in_game(True)
    # raised catwalk: the passage she leads you along
    K.deck("Cat", 5150, 6600, -700, -450, 324, g, e, W); legs("Cat", [(x, y) for x in (5170, 5520, 5880, 6240, 6580) for y in (-690, -460)], 298)
    K.railing("Cat_RailS", [(5150, -698, 324), (6600, -698, 324)], r, W); K.railing("Cat_RailN", [(5150, -452, 324), (6600, -452, 324)], r, W)
    for i, x in enumerate((5200, 5900, 6550)): K.bar(f"Cat_tie{i}", (x, -700, 310), (x, -800, 310), 8, 8, e, W, shadow=False)
    # stair down from the catwalk's far end
    K.stairs("Cat_StairDown", 7000, 6600, -690, -460, 0, 324, g, e, W)
    K.railing("Cat_StairRail", [(6600, -462, 324), (7000, -462, 0)], r, W, collide_wall=False)
    # the high ledge (cliff memory): hangs from the roof trusses
    K.deck("Ledge", 6250, 6600, -795, -355, 750, g, e, W); rods("Ledge", [(6260, -785), (6590, -785), (6260, -365), (6590, -365)], 750, 1090)
    K.railing("Ledge_RailN", [(6250, -357, 750), (6600, -357, 750)], r, W); K.railing("Ledge_RailE", [(6598, -357, 750), (6598, -793, 750)], r, W)
    K.railing("Ledge_RailW_a", [(6252, -357, 750), (6252, -470, 750)], r, W, collide_wall=False); K.railing("Ledge_RailW_b", [(6252, -690, 750), (6252, -793, 750)], r, W, collide_wall=False)
    # nave: broken catwalk by the exit
    K.deck("Exit", 9100, 9800, 800, 1050, 474, g, e, W); legs("Exit", [(x, y) for x in (9120, 9450, 9780) for y in (812,)], 448)
    K.railing("Exit_Rail", [(9100, 802, 474), (9800, 802, 474)], r, W, collide_wall=False)
    return "ok"
def info():
    out = {}
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.PostProcessVolume):
            st = a.get_editor_property("settings"); o = {}
            for k in ("auto_exposure_method", "auto_exposure_bias", "auto_exposure_min_brightness", "auto_exposure_max_brightness", "override_auto_exposure_bias", "override_auto_exposure_min_brightness", "override_auto_exposure_max_brightness", "bloom_intensity", "vignette_intensity"):
                try: o[k] = str(st.get_editor_property(k))
                except Exception as ex: o[k] = "?"
            out[a.get_actor_label()] = o; out[a.get_actor_label() + "_unbound"] = bool(a.get_editor_property("unbound"))
    for k in ("brick", "conc", "roof", "floor", "steel"):
        m = M[k]; par = m.get_editor_property("parent") if isinstance(m, unreal.MaterialInstanceConstant) else None
        out["mat_" + k] = [m.get_name(), par.get_name() if par else None] + [str(n) for n in unreal.MaterialEditingLibrary.get_scalar_parameter_names(m)][:8]
    return out
def run(only=None):
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_FactoryHub")
    step("materials", materials)
    for n, f in (("cleanup", cleanup), ("rematerial", rematerial), ("shell", shell), ("structure", structure), ("lights", lights), ("walkways", walkways)):
        if only is None or n in only: step(n, f)
    step("info", info)
    n = sum(1 for a in E.get_all_level_actors() if unreal.Name(K.TAG) in a.tags); res["fac2_actors"] = n
    if not res["err"]: L.save_current_level()
    return res
