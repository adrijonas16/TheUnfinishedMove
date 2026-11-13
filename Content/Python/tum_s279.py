# Fix pass from playtest feedback: real skies, one chair, factory door/stairs/props/no cloth, dragon cloud sea + supported gates
import unreal, math, random, traceback
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; MAT = "/Game/TUM/Materials/Sky"; DC = "/Game/DerelictCorridor/Assets/Fab/Megascans/3D"; MS = "/Game/MS/3D"
INV = "/Game/TUM/Materials/Surfaces/M_Invisible"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a
def first(folder):
    ps = [p for p in EAL.list_assets(folder, False, False) if p.split("/")[-1].startswith("SM_")]
    if not ps: raise RuntimeError("no SM in " + folder)
    return EAL.load_asset(ps[0])
def ex(m, cls, x, y, **kw):
    e = MEL.create_material_expression(m, cls, x, y)
    for k, v in kw.items(): e.set_editor_property(k, v)
    return e
def con(a, ao, b, bi): MEL.connect_material_expressions(a, ao, b, bi)
def lc(r, g, b): return unreal.LinearColor(r, g, b, 1)

# ---------------- sky materials ----------------
def sky_master():
    p = f"{MAT}/M_SkyDome"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_SkyDome", MAT, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT); m.set_editor_property("two_sided", True)
    wp = ex(m, unreal.MaterialExpressionWorldPosition, -2400, 0); op = ex(m, unreal.MaterialExpressionObjectPositionWS, -2400, 150)
    sub = ex(m, unreal.MaterialExpressionSubtract, -2200, 50); con(wp, "", sub, "A"); con(op, "", sub, "B")
    nrm = ex(m, unreal.MaterialExpressionNormalize, -2050, 50); con(sub, "", nrm, "")
    z = ex(m, unreal.MaterialExpressionComponentMask, -1900, 0, b=True); con(nrm, "", z, "")
    xy = ex(m, unreal.MaterialExpressionComponentMask, -1900, 150, r=True, g=True); con(nrm, "", xy, "")
    zc = ex(m, unreal.MaterialExpressionSaturate, -1750, 0); con(z, "", zc, "")
    # gradient horizon -> zenith
    pw = ex(m, unreal.MaterialExpressionPower, -1600, 0, const_exponent=0.55); con(zc, "", pw, "Base")
    hor = ex(m, unreal.MaterialExpressionVectorParameter, -1600, -250, parameter_name="HorizonColor", default_value=lc(0.06, 0.035, 0.03))
    zen = ex(m, unreal.MaterialExpressionVectorParameter, -1600, -120, parameter_name="ZenithColor", default_value=lc(0.004, 0.007, 0.018))
    grad = ex(m, unreal.MaterialExpressionLinearInterpolate, -1350, -150); con(hor, "", grad, "A"); con(zen, "", grad, "B"); con(pw, "", grad, "Alpha")
    # sky-projected clouds: uv = xy / (z + 0.2)
    zb = ex(m, unreal.MaterialExpressionAdd, -1750, 250, const_b=0.22); con(zc, "", zb, "A")
    dv = ex(m, unreal.MaterialExpressionDivide, -1600, 200); con(xy, "", dv, "A"); con(zb, "", dv, "B")
    tl = ex(m, unreal.MaterialExpressionScalarParameter, -1600, 350, parameter_name="CloudTiling", default_value=0.6)
    mu = ex(m, unreal.MaterialExpressionMultiply, -1450, 250); con(dv, "", mu, "A"); con(tl, "", mu, "B")
    pan = ex(m, unreal.MaterialExpressionPanner, -1300, 250, speed_x=0.004, speed_y=0.0015); con(mu, "", pan, "Coordinate")
    tex = ex(m, unreal.MaterialExpressionTextureSample, -1100, 250, texture=EAL.load_asset("/Engine/EngineSky/T_Sky_Clouds_M"), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    con(pan, "", tex, "UVs")
    pan2 = ex(m, unreal.MaterialExpressionPanner, -1300, 450, speed_x=-0.002, speed_y=0.003); con(mu, "", pan2, "Coordinate")
    tex2 = ex(m, unreal.MaterialExpressionTextureSample, -1100, 450, texture=EAL.load_asset("/Engine/EngineSky/T_Sky_Clouds_M"), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    con(pan2, "", tex2, "UVs")
    cr = ex(m, unreal.MaterialExpressionComponentMask, -900, 250, r=True); con(tex, "RGB", cr, "")
    cg = ex(m, unreal.MaterialExpressionComponentMask, -900, 450, g=True); con(tex2, "RGB", cg, "")
    cm = ex(m, unreal.MaterialExpressionMultiply, -750, 350); con(cr, "", cm, "A"); con(cg, "", cm, "B")
    cov = ex(m, unreal.MaterialExpressionScalarParameter, -750, 500, parameter_name="CloudAmount", default_value=1.8)
    cm2 = ex(m, unreal.MaterialExpressionMultiply, -600, 350); con(cm, "", cm2, "A"); con(cov, "", cm2, "B")
    fade = ex(m, unreal.MaterialExpressionPower, -750, 600, const_exponent=0.35); con(zc, "", fade, "Base")
    cm3 = ex(m, unreal.MaterialExpressionMultiply, -450, 400); con(cm2, "", cm3, "A"); con(fade, "", cm3, "B")
    ca = ex(m, unreal.MaterialExpressionSaturate, -300, 400); con(cm3, "", ca, "")
    ccol = ex(m, unreal.MaterialExpressionVectorParameter, -450, 150, parameter_name="CloudColor", default_value=lc(0.05, 0.045, 0.05))
    mix = ex(m, unreal.MaterialExpressionLinearInterpolate, -150, 0); con(grad, "", mix, "A"); con(ccol, "", mix, "B"); con(ca, "", mix, "Alpha")
    # stars above the clouds (night only, via StarAmount)
    st = ex(m, unreal.MaterialExpressionTextureSample, -1100, 700, texture=EAL.load_asset("/Engine/EngineSky/T_Sky_Stars"), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    sm = ex(m, unreal.MaterialExpressionMultiply, -1300, 700, const_b=3.0); con(dv, "", sm, "A"); con(sm, "", st, "UVs")
    sa = ex(m, unreal.MaterialExpressionScalarParameter, -900, 850, parameter_name="StarAmount", default_value=0.0)
    oc = ex(m, unreal.MaterialExpressionOneMinus, -750, 750); con(ca, "", oc, "")
    s1 = ex(m, unreal.MaterialExpressionMultiply, -600, 700); con(st, "RGB", s1, "A"); con(sa, "", s1, "B")
    s2 = ex(m, unreal.MaterialExpressionMultiply, -450, 700); con(s1, "", s2, "A"); con(oc, "", s2, "B")
    s3 = ex(m, unreal.MaterialExpressionMultiply, -300, 700); con(s2, "", s3, "A"); con(zc, "", s3, "B")
    add = ex(m, unreal.MaterialExpressionAdd, 0, 100); con(mix, "", add, "A"); con(s3, "", add, "B")
    br = ex(m, unreal.MaterialExpressionScalarParameter, 0, 300, parameter_name="Brightness", default_value=1.0)
    fin = ex(m, unreal.MaterialExpressionMultiply, 150, 100); con(add, "", fin, "A"); con(br, "", fin, "B")
    MEL.connect_material_property(fin, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def sky_mi(name, **p):
    path = f"{MAT}/{name}"
    mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else AT.create_asset(name, MAT, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, EAL.load_asset(f"{MAT}/M_SkyDome"))
    for k, v in p.items():
        if isinstance(v, tuple): MEL.set_material_instance_vector_parameter_value(mi, k, lc(*v))
        else: MEL.set_material_instance_scalar_parameter_value(mi, k, float(v))
    EAL.save_loaded_asset(mi, False); return mi
def cloud_sea():
    p = f"{MAT}/M_CloudSea"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_CloudSea", MAT, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    wp = ex(m, unreal.MaterialExpressionWorldPosition, -1400, 0)
    xy = ex(m, unreal.MaterialExpressionComponentMask, -1250, 0, r=True, g=True); con(wp, "", xy, "")
    d = ex(m, unreal.MaterialExpressionDivide, -1100, 0, const_b=9000.0); con(xy, "", d, "A")
    out = []
    for i, (sx, sy, sc) in enumerate(((0.01, 0.004, 1.0), (-0.006, 0.008, 2.3))):
        mm = ex(m, unreal.MaterialExpressionMultiply, -950, i * 200, const_b=sc); con(d, "", mm, "A")
        pn = ex(m, unreal.MaterialExpressionPanner, -800, i * 200, speed_x=sx, speed_y=sy); con(mm, "", pn, "Coordinate")
        t = ex(m, unreal.MaterialExpressionTextureSample, -600, i * 200, texture=EAL.load_asset("/Engine/EngineSky/T_Sky_Clouds_M")); con(pn, "", t, "UVs")
        c = ex(m, unreal.MaterialExpressionComponentMask, -400, i * 200, r=(i == 0), g=(i == 1)); con(t, "RGB", c, ""); out.append(c)
    a = ex(m, unreal.MaterialExpressionAdd, -250, 100); con(out[0], "", a, "A"); con(out[1], "", a, "B")
    s = ex(m, unreal.MaterialExpressionSaturate, -100, 100); con(a, "", s, "")
    lo = ex(m, unreal.MaterialExpressionVectorParameter, -250, -200, parameter_name="Low", default_value=lc(0.35, 0.3, 0.3))
    hi = ex(m, unreal.MaterialExpressionVectorParameter, -250, -350, parameter_name="High", default_value=lc(1.4, 1.2, 1.05))
    l = ex(m, unreal.MaterialExpressionLinearInterpolate, 50, 0); con(lo, "", l, "A"); con(hi, "", l, "B"); con(s, "", l, "Alpha")
    MEL.connect_material_property(l, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def skies():
    sky_master(); cloud_sea()
    sky_mi("MI_Sky_RainyNight", HorizonColor=(0.09, 0.05, 0.035), ZenithColor=(0.006, 0.009, 0.022), CloudColor=(0.06, 0.05, 0.055), CloudAmount=2.4, StarAmount=0.0, Brightness=1.0)
    sky_mi("MI_Sky_FactoryNight", HorizonColor=(0.05, 0.06, 0.075), ZenithColor=(0.004, 0.008, 0.02), CloudColor=(0.035, 0.04, 0.05), CloudAmount=1.6, StarAmount=0.35, Brightness=1.0)
    sky_mi("MI_Sky_DragonDusk", HorizonColor=(1.6, 0.75, 0.38), ZenithColor=(0.12, 0.2, 0.42), CloudColor=(1.2, 0.85, 0.7), CloudAmount=1.5, StarAmount=0.0, Brightness=1.0, CloudTiling=0.45)
    sky_mi("MI_Sky_CliffDawn", HorizonColor=(0.9, 0.75, 0.65), ZenithColor=(0.18, 0.28, 0.5), CloudColor=(0.95, 0.9, 0.9), CloudAmount=1.4, Brightness=1.0)
    sky_mi("MI_Sky_WarDusk", HorizonColor=(1.1, 0.42, 0.18), ZenithColor=(0.07, 0.07, 0.12), CloudColor=(0.35, 0.18, 0.12), CloudAmount=2.2, Brightness=1.0)
    return "ok"
def put_dome(mi_name, radius=400000.0, center=(0, 0, 0), label="Sky_Dome"):
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() == label: E.destroy_actor(a)
    m = EAL.load_asset("/Engine/BasicShapes/Sphere")
    a = E.spawn_actor_from_object(m, V(*center), unreal.Rotator())
    a.set_actor_scale3d(V(radius / 50, radius / 50, radius / 50)); a.static_mesh_component.set_material(0, EAL.load_asset(f"{MAT}/{mi_name}"))
    a.set_actor_enable_collision(False); a.static_mesh_component.set_cast_shadow(False)
    a.set_actor_label(label); a.set_folder_path("Lighting"); return a

# ---------------- room ----------------
def room():
    L.load_level("/Game/TUM/Maps/M_RealRoom")
    ch = find("Desk_Chair")
    if ch: E.destroy_actor(ch)
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name() == "Sphere":
            a.static_mesh_component.set_material(0, EAL.load_asset(f"{MAT}/MI_Sky_RainyNight"))
    seat = find("Seat_Point"); sx, sy = 2.0, 264.0
    seat.set_actor_location(V(sx, sy, 96), False, False); seat.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=-90), False)
    d = find("IntroDirector"); d.set_editor_property("Chair", seat)
    def aim(name, loc, look, fov):
        a = find(name)
        if not a: return
        a.set_actor_location(V(*loc), False, False); dd = [look[i] - loc[i] for i in range(3)]
        a.set_actor_rotation(unreal.Rotator(roll=0, pitch=math.degrees(math.atan2(dd[2], math.hypot(dd[0], dd[1]))), yaw=math.degrees(math.atan2(dd[1], dd[0]))), False)
        a.get_cine_camera_component().set_editor_property("current_focal_length", 36.0 / (2 * math.tan(math.radians(fov / 2))))
    aim("Cine_Seat", (75, 292, 168), (-15, 190, 92), 72)
    aim("Cine_Ear", (-130, 140, 138), (0, 258, 112), 55)
    aim("Cine_1", (-62, 205, 128), (0, 262, 122), 42)
    h = find("Hint_Sit")
    if h: h.set_actor_location(V(sx, 200, 118), False, False)
    h = find("Hint_Earbuds")
    if h: h.set_actor_location(V(-40, 170, 100), False, False)
    L.save_current_level(); return "ok"

# ---------------- factory ----------------
def stack(name, box, tags, folder="Art/Factory/Stacks"):
    """Pile of rusty steel beams + planks filling a walkable block (graybox keeps collision, becomes invisible)."""
    beam = first(f"{DC}/Ind_Con_Supplies_Beam_Metal_Rusty_02"); plank = first(f"{DC}/Ind_Con_Supplies_Plank_Wood_Long_01")
    (cx, cy, cz), (sx, sy, sz) = box
    out = []
    layers = max(1, int(sz / 22))
    along_x = sx >= sy
    L_ = sx if along_x else sy; W_ = sy if along_x else sx
    random.seed(hash(name) & 0xffff)
    for li in range(layers):
        k = max(2, int(W_ / 30))
        for i in range(k):
            off = -W_ / 2 + (i + 0.5) * W_ / k
            mesh = plank if li == layers - 1 else beam
            z = cz - sz / 2 + (li + 0.5) * sz / layers
            yaw = (0 if along_x else 90) + random.uniform(-3, 3)
            a = E.spawn_actor_from_object(mesh, V(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
            o, e = a.get_actor_bounds(False)
            s = [L_ * random.uniform(0.92, 1.02) / max(2 * e.x if along_x else 2 * e.y, 1), W_ / k * 0.95 / max(2 * e.y if along_x else 2 * e.x, 1), sz / layers / max(2 * e.z, 1)]
            if not along_x: s[0], s[1] = s[1], s[0]
            a.set_actor_scale3d(V(*s))
            o, e = a.get_actor_bounds(False); l = a.get_actor_location()
            px, py = (cx + random.uniform(-6, 6), cy + off) if along_x else (cx + off, cy + random.uniform(-6, 6))
            a.set_actor_location(V(l.x + px - o.x, l.y + py - o.y, l.z + z - o.z), False, False)
            a.set_actor_enable_collision(False); a.tags = list(tags); a.set_actor_label(f"{name}_{li}_{i}"); a.set_folder_path(folder); out.append(a)
    return out
def bx(a):
    o, e = a.get_actor_bounds(False); return (o.x, o.y, o.z), (2 * e.x, 2 * e.y, 2 * e.z)
def invisible(a):
    m = EAL.load_asset(INV)
    for i in range(a.static_mesh_component.get_num_materials()): a.static_mesh_component.set_material(i, m)
def factory():
    L.load_level("/Game/TUM/Maps/M_FactoryHub")
    out = {}
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label()
        if lab.startswith(("Cloth_Hang_", "Cover_Entry", "Cover_DragonStep", "Cover_Catwalk_Stairs", "Cover_Exit", "Skin_PatrolGuard", "Prop_", "Door_")) or str(a.get_folder_path()).startswith("Art/Factory/Stacks"):
            E.destroy_actor(a)
    # steps / stairs: steel beam piles (DragonLift ones appear with the graybox when the dragon is done)
    for n in ("Entry_BrokenStair", "Catwalk_Stairs", "Exit_ExposePiece_Hatch", "DragonStep_0", "DragonStep_1", "DragonStep_2"):
        a = find(n)
        if not a: continue
        tags = [str(t) for t in a.tags if str(t) in ("DragonLift", "Exit_ExposePiece")]
        a.set_actor_hidden_in_game(False) if not tags else None
        invisible(a)
        pieces = stack(f"Stack_{n}", bx(a), tags)
        if tags:
            for p in pieces: p.set_actor_hidden_in_game(True)
        out[n] = len(pieces)
    # patrol is just a moving searchlight now (no walking figure)
    # entrance door behind the spawn
    door = first(f"{MS}/Old_Wooden_Door_uflvddofa")
    for i, (y, yaw) in enumerate(((-130, 0), (130, 180))):
        d = E.spawn_actor_from_object(door, V(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=90 + (0 if i == 0 else 180)))
        o, e = d.get_actor_bounds(False)
        s = 520.0 / max(2 * e.z, 1); d.set_actor_scale3d(V(s, s, s))
        o, e = d.get_actor_bounds(False); l = d.get_actor_location()
        d.set_actor_location(V(l.x + (-312) - o.x, l.y + y - o.y, l.z + e.z - o.z), False, False)
        d.set_actor_label(f"Door_Entrance_{i}"); d.set_folder_path("Art/Factory/Door")
    # structure: zones along the hall walls (never in rows), each with its own kind of junk
    random.seed(77)
    zones = [  # (x0, x1, kind list)
        (200, 1500, ["Ind_Ware_Storage_Shelf_Metal_Rusted_01", "Ind_Ware_Storage_Cabinet_Metal_Rusty_01", "Ind_Ware_Equipment_Ladder_Metal_Worn_01", "Ind_Ware_Equipment_Handtruck_Metal_Worn_01"]),
        (1500, 4000, ["Ind_Ware_Furn_Table_Wood_Worn_01", "Res_Furn_Stool_Metal_Worn_01", "Res_Furn_Chair_Metal_Armless_01", "Ind_OW_Equipment_Toolbox_Metal_Green_01", "Ind_Ware_Equipment_Cable_Rubber_Black_01"]),
        (4000, 6000, ["Ind_Ware_Cabinet_Electric_Metal_Dirty_01", "Ind_Fact_Panel_ElectricalBox_Metal_Worn_01", "Ind_Aba_Box_Electric_Metal_Worn_01", "Urb_Street_ElectricalBox_Metal_Worn_02", "Ind_Set_Pipe_Metal_Mod_01"]),
        (6000, 7300, ["Ind_AbaFact_Tank_Gas_Metal_Worn_02", "Ind_Container_Metal_Set_01", "Ind_Rubble_Debris_Plank_Wood_Broken_01", "Urb_Road_Sheet_Metal_Rusty_03"]),
    ]
    n = 0
    for x0, x1, kinds in zones:
        meshes = []
        for k in kinds:
            try: meshes.append(first(f"{DC}/{k}"))
            except Exception: pass
        for side in (-1, 1):
            x = x0 + random.uniform(0, 250)
            while x < x1:
                m = random.choice(meshes)
                y = side * random.uniform(640, 760)
                a = E.spawn_actor_from_object(m, V(x, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=(90 if side < 0 else -90) + random.uniform(-25, 25)))
                o, e = a.get_actor_bounds(False); l = a.get_actor_location()
                a.set_actor_location(V(l.x, l.y - (o.y + side * e.y - y) * 0 , l.z + (0 - (o.z - e.z))), False, False)
                a.set_actor_label(f"Prop_{n}"); a.set_folder_path("Art/Factory/Zones"); n += 1
                x += random.uniform(260, 520)
    out["props"] = n
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name() == "Sphere":
            a.static_mesh_component.set_material(0, EAL.load_asset(f"{MAT}/MI_Sky_FactoryNight"))
    L.save_current_level(); return out

# ---------------- dragon ----------------
def dragon():
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon")
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(("CloudSea_Plane", "GateRock_")): E.destroy_actor(a)
    put_dome("MI_Sky_DragonDusk", 600000.0, (5000, 0, 0))
    p = E.spawn_actor_from_object(EAL.load_asset("/Engine/BasicShapes/Plane"), V(6000, 0, 700), unreal.Rotator())
    p.set_actor_scale3d(V(2500, 2500, 1)); p.static_mesh_component.set_material(0, EAL.load_asset(f"{MAT}/M_CloudSea"))
    p.set_actor_enable_collision(False); p.static_mesh_component.set_cast_shadow(False); p.set_actor_label("CloudSea_Plane"); p.set_folder_path("Art/Dragon")
    rock = first(f"{MS}/Nordic_Beach_Rock_Formation_vd4iecjva")
    for g in range(3):
        gate = find(f"Gate_{g}")
        if not gate: continue
        o, e = gate.get_actor_bounds(False)
        for side in (-1, 1):
            a = E.spawn_actor_from_object(rock, V(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360)))
            oo, ee = a.get_actor_bounds(False)
            top = o.z - e.z + 80; h = top - 300
            a.set_actor_scale3d(V(260 / max(2 * ee.x, 1), 260 / max(2 * ee.y, 1), h / max(2 * ee.z, 1)))
            oo, ee = a.get_actor_bounds(False); l = a.get_actor_location()
            a.set_actor_location(V(l.x + o.x - oo.x, l.y + side * (e.y + 60) - oo.y, l.z + (300 + h / 2) - oo.z), False, False)
            a.set_actor_enable_collision(False); a.set_actor_label(f"GateRock_{g}_{side}"); a.set_folder_path("Art/Dragon/Gates")
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.ExponentialHeightFog):
            sd = a.component.get_editor_property("second_fog_data"); sd.set_editor_property("fog_density", 0.25); a.component.set_editor_property("second_fog_data", sd)
            a.component.set_fog_density(0.006)
    L.save_current_level(); return "ok"

def cliffwar():
    out = {}
    for mp, mi in (("M_Cut_Cliff", "MI_Sky_CliffDawn"), ("M_Cut_WarField", "MI_Sky_WarDusk")):
        L.load_level(f"/Game/TUM/Maps/{mp}"); put_dome(mi, 500000.0, (3000, 0, 0)); L.save_current_level(); out[mp] = "dome"
    return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("skies", skies)
    for n, f in (("room", room), ("factory", factory), ("dragon", dragon), ("cliffwar", cliffwar)): step(n, f)
    return res
