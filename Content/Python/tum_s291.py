# Dragon world: a Nordic fjord at dusk. Take off from a sea cliff, climb through broken clouds, then the obstacle run above them.
import unreal, math, random, traceback, importlib
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; MS = "/Game/MS/3D"; SKY = "/Game/TUM/Materials/Sky"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a
def sms(folder):
    return [EAL.load_asset(p) for p in EAL.list_assets(folder, False, False) if p.split("/")[-1].startswith("SM_")]
def place(mesh, name, x, y, z_top, h, yaw, folder, collide=False, w=None):
    a = E.spawn_actor_from_object(mesh, V(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    o, e = a.get_actor_bounds(False)
    s = h / max(2 * e.z, 1); sxy = (w / max(2 * max(e.x, e.y), 1)) if w else s
    a.set_actor_scale3d(V(sxy, sxy, s))
    o, e = a.get_actor_bounds(False); l = a.get_actor_location()
    a.set_actor_location(V(l.x + x - o.x, l.y + y - o.y, l.z + (z_top - e.z) - o.z), False, False)
    if not collide: a.set_actor_enable_collision(False)
    a.set_actor_label(name); a.set_folder_path(folder); return a
def ex(m, cls, x, y, **kw):
    e = MEL.create_material_expression(m, cls, x, y)
    for k, v in kw.items(): e.set_editor_property(k, v)
    return e
def con(a, ao, b, bi): MEL.connect_material_expressions(a, ao, b, bi)

def materials():
    # sea
    p = f"{SKY}/M_Sea"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_Sea", SKY, unreal.Material, unreal.MaterialFactoryNew())
    wp = ex(m, unreal.MaterialExpressionWorldPosition, -1200, 0); xy = ex(m, unreal.MaterialExpressionComponentMask, -1050, 0, r=True, g=True); con(wp, "", xy, "")
    d = ex(m, unreal.MaterialExpressionDivide, -900, 0, const_b=2500.0); con(xy, "", d, "A")
    pn = ex(m, unreal.MaterialExpressionPanner, -750, 0, speed_x=0.01, speed_y=0.006); con(d, "", pn, "Coordinate")
    t = ex(m, unreal.MaterialExpressionTextureSample, -550, 0, texture=EAL.load_asset("/Engine/EngineSky/T_Sky_Clouds_M")); con(pn, "", t, "UVs")
    r = ex(m, unreal.MaterialExpressionComponentMask, -350, 0, r=True); con(t, "RGB", r, "")
    c1 = ex(m, unreal.MaterialExpressionConstant3Vector, -350, -250, constant=unreal.LinearColor(0.004, 0.018, 0.028, 1))
    c2 = ex(m, unreal.MaterialExpressionConstant3Vector, -350, -120, constant=unreal.LinearColor(0.02, 0.05, 0.06, 1))
    lp = ex(m, unreal.MaterialExpressionLinearInterpolate, -150, -150); con(c1, "", lp, "A"); con(c2, "", lp, "B"); con(r, "", lp, "Alpha")
    MEL.connect_material_property(lp, "", unreal.MaterialProperty.MP_BASE_COLOR)
    ro = ex(m, unreal.MaterialExpressionConstant, -150, 100, r=0.07); MEL.connect_material_property(ro, "", unreal.MaterialProperty.MP_ROUGHNESS)
    sp = ex(m, unreal.MaterialExpressionConstant, -150, 180, r=0.9); MEL.connect_material_property(sp, "", unreal.MaterialProperty.MP_SPECULAR)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False)
    # broken cloud layer: translucent, see the world through the gaps
    p = f"{SKY}/M_CloudLayer"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_CloudLayer", SKY, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT); m.set_editor_property("two_sided", True)
    wp = ex(m, unreal.MaterialExpressionWorldPosition, -1400, 0); xy = ex(m, unreal.MaterialExpressionComponentMask, -1250, 0, r=True, g=True); con(wp, "", xy, "")
    d = ex(m, unreal.MaterialExpressionDivide, -1100, 0, const_b=14000.0); con(xy, "", d, "A")
    outs = []
    for i, (sx, sy, sc) in enumerate(((0.008, 0.003, 1.0), (-0.004, 0.006, 2.1))):
        mm = ex(m, unreal.MaterialExpressionMultiply, -950, i * 200, const_b=sc); con(d, "", mm, "A")
        pn = ex(m, unreal.MaterialExpressionPanner, -800, i * 200, speed_x=sx, speed_y=sy); con(mm, "", pn, "Coordinate")
        t = ex(m, unreal.MaterialExpressionTextureSample, -600, i * 200, texture=EAL.load_asset("/Engine/EngineSky/T_Sky_Clouds_M")); con(pn, "", t, "UVs")
        c = ex(m, unreal.MaterialExpressionComponentMask, -400, i * 200, r=(i == 0), g=(i == 1)); con(t, "RGB", c, ""); outs.append(c)
    mu = ex(m, unreal.MaterialExpressionMultiply, -250, 100); con(outs[0], "", mu, "A"); con(outs[1], "", mu, "B")
    k = ex(m, unreal.MaterialExpressionMultiply, -100, 100, const_b=3.2); con(mu, "", k, "A")
    sub = ex(m, unreal.MaterialExpressionSubtract, 0, 100, const_b=0.25); con(k, "", sub, "A")
    sat = ex(m, unreal.MaterialExpressionSaturate, 100, 100); con(sub, "", sat, "")
    MEL.connect_material_property(sat, "", unreal.MaterialProperty.MP_OPACITY)
    lo = ex(m, unreal.MaterialExpressionConstant3Vector, -100, -250, constant=unreal.LinearColor(0.9, 0.62, 0.5, 1))
    hi = ex(m, unreal.MaterialExpressionConstant3Vector, -100, -120, constant=unreal.LinearColor(2.2, 1.6, 1.25, 1))
    lp = ex(m, unreal.MaterialExpressionLinearInterpolate, 150, -150); con(lo, "", lp, "A"); con(hi, "", lp, "B"); con(sat, "", lp, "Alpha")
    MEL.connect_material_property(lp, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False)
    return "ok"

SEA_Z = -2600.0
def world():
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon")
    for a in list(E.get_all_level_actors()):
        if str(a.get_folder_path()).startswith("Art/Dragon/World") or a.get_actor_label() in ("CloudSea_Plane", "Sea_Plane", "Start_Floor", "Kill_Floor"):
            E.destroy_actor(a)
    random.seed(1312)
    F = "Art/Dragon/World"
    sea = E.spawn_actor_from_object(EAL.load_asset("/Engine/BasicShapes/Plane"), V(3000, 0, SEA_Z), unreal.Rotator())
    sea.set_actor_scale3d(V(3000, 3000, 1)); sea.static_mesh_component.set_material(0, EAL.load_asset(f"{SKY}/M_Sea")); sea.set_actor_enable_collision(False); sea.set_actor_label("Sea_Plane"); sea.set_folder_path(F)
    cl = E.spawn_actor_from_object(EAL.load_asset("/Engine/BasicShapes/Plane"), V(6000, 0, 400), unreal.Rotator())
    cl.set_actor_scale3d(V(3000, 3000, 1)); cl.static_mesh_component.set_material(0, EAL.load_asset(f"{SKY}/M_CloudLayer")); cl.set_actor_enable_collision(False)
    cl.static_mesh_component.set_cast_shadow(False); cl.set_actor_label("CloudSea_Plane"); cl.set_folder_path(F)
    massive = sms(f"{MS}/Massive_Nordic_Coastal_Cliff_ullqbb1ga") + sms(f"{MS}/Massive_Nordic_Coastal_Cliff_vdssailfa") + sms(f"{MS}/Massive_Nordic_Coastal_Cliff_vefkehbva") + sms(f"{MS}/Massive_Nordic_Coastal_Cliff_veqnci0db")
    huge = sms(f"{MS}/Huge_Nordic_Coastal_Cliff_ulkiejkva") + sms(f"{MS}/Huge_Nordic_Coastal_Cliff_venrdcgga") + sms(f"{MS}/Nordic_Coastal_Cliff_ulmiccava")
    stacks = sms(f"{MS}/Nordic_Beach_Rock_Formation_vd4iecjva") + sms(f"{MS}/Nordic_Beach_Rock_Formation_vckqccbga") + sms(f"{MS}/Nordic_Beach_Rock_Formation_vfgkajyga")
    n = 0
    # fjord walls on both sides, irregular, rising from the sea to below the cloud layer
    for side in (-1, 1):
        x = -12000
        while x < 18000:
            y = side * random.uniform(3200, 5200); top = random.uniform(-600, 900)
            place(random.choice(massive + huge), f"Fjord_{n}", x, y, top, top - SEA_Z + 400, random.uniform(0, 360), F, w=random.uniform(2600, 4200)); n += 1
            x += random.uniform(1600, 2600)
    # sea stacks in the fjord, below the flight path
    for i in range(16):
        x = random.uniform(-9000, 15000); y = random.uniform(-2500, 2500)
        if x < -6500 and abs(y) < 1200: continue
        top = random.uniform(-1600, -200)
        place(random.choice(stacks), f"SeaStack_{i}", x, y, top, top - SEA_Z + 200, random.uniform(0, 360), F, w=random.uniform(500, 1100))
    # take-off cliff with a ruined watchtower
    start = place(massive[0], "Start_Cliff", -8300, 0, -1400, 1400, 30, F, w=2600)
    ground = sms(f"{MS}/Nordic_Beach_Rocky_Ground_ukoncdamw")
    flat = [g for g in ground if "Flat" in g.get_name()] or ground
    place(flat[0], "Start_Top", -8100, 0, -1395, 40, 0, F, w=1400)
    fl = E.spawn_actor_from_object(EAL.load_asset("/Engine/BasicShapes/Cube"), V(-8100, 0, -1440), unreal.Rotator())
    fl.set_actor_scale3d(V(12, 12, 0.9)); fl.static_mesh_component.set_material(0, EAL.load_asset("/Game/TUM/Materials/Surfaces/M_Invisible")); fl.set_actor_label("Start_Floor"); fl.set_folder_path(F)
    arch = sms(f"{MS}/Modular_Church_Ruin_Stone_Arch_02_xjurabvs"); col = sms(f"{MS}/Medieval_Church_Ruin_Column_01_xjsofces") + sms(f"{MS}/Medieval_Church_Ruin_Column_02_xjtrfc1s")
    walls = sms(f"{MS}/Modular_Ruins_Wall_vdcjbgo") + sms(f"{MS}/Modular_ChurchRuin_Stone_Kit_yh3kddhiy")
    place(arch[0], "Start_Arch", -8650, 250, -400, 1000, 90, F)
    place(col[0], "Start_Col_0", -8550, -500, -500, 900, 10, F)
    place(walls[0], "Start_Wall_0", -8800, -350, -1050, 380, 80, F)
    trees = sms(f"{MS}/Dead_Tree_rlthg")
    if trees: place(trees[0], "Start_Tree", -7750, 520, -900, 520, 40, F)
    # ruins on fjord tops so the world below has a story
    for i in range(7):
        x = random.uniform(-6000, 14000); y = random.choice((-1, 1)) * random.uniform(3400, 4600)
        place(random.choice(arch + col), f"FjordRuin_{i}", x, y, random.uniform(200, 1100), random.uniform(700, 1300), random.uniform(0, 360), F)
    # move spawn + bounds to include the climb
    ps = [a for a in E.get_all_level_actors() if isinstance(a, unreal.PlayerStart)][0]
    ps.set_actor_location(V(-8100, 0, -1300), False, False)
    for nme, cx, ex_ in (("Bound_N", 2000, 11000), ("Bound_S", 2000, 11000), ("Bound_High", 2000, 11000)):
        b = find(nme); o, e = b.get_actor_bounds(False); s = b.get_actor_scale3d()
        b.set_actor_scale3d(V(s.x * ex_ / e.x, s.y, s.z)); o, e = b.get_actor_bounds(False); l = b.get_actor_location()
        b.set_actor_location(V(l.x + cx - o.x, l.y, l.z), False, False)
    bb = find("Bound_Back"); l = bb.get_actor_location(); bb.set_actor_location(V(-9100, l.y, -500), False, False)
    s = bb.get_actor_scale3d(); bb.set_actor_scale3d(V(s.x, s.y, s.z * 2.2))
    bl = find("Bound_Low"); o, e = bl.get_actor_bounds(False); s = bl.get_actor_scale3d()
    bl.set_actor_scale3d(V(s.x * 6500 / e.x, s.y, s.z)); o, e = bl.get_actor_bounds(False); l = bl.get_actor_location(); bl.set_actor_location(V(l.x + 6600 - o.x, l.y, l.z), False, False)
    kf = E.spawn_actor_from_object(EAL.load_asset("/Engine/BasicShapes/Cube"), V(-4500, 0, -2100), unreal.Rotator())
    kf.set_actor_scale3d(V(95, 25, 1)); kf.static_mesh_component.set_material(0, EAL.load_asset("/Game/TUM/Materials/Surfaces/M_Invisible")); kf.set_actor_label("Kill_Floor"); kf.set_folder_path(F)
    # dragon starts perched on the cliff: move the mount relative to the new spawn
    dm = find("Dragon_Mesh"); dl = dm.get_actor_location(); dm.set_actor_location(V(dl.x - 8100, dl.y, dl.z - 3300), False, False)
    hb = find("Hint_Boost")
    if hb: hb.set_actor_location(V(-7300, 0, -1000), False, False)
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.ExponentialHeightFog):
            sd = a.component.get_editor_property("second_fog_data"); sd.set_editor_property("fog_density", 0.0); a.component.set_editor_property("second_fog_data", sd)
            a.component.set_fog_density(0.0035); a.component.set_fog_height_falloff(0.0005) if hasattr(a.component, "set_fog_height_falloff") else None
            a.set_actor_location(V(0, 0, SEA_Z), False, False)
    L.save_current_level(); return {"fjord": n}

def route():
    import tum_dragonroute as D; importlib.reload(D)
    return str(D.run())[:500]

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("materials", materials); step("route", route); step("world", world)
    return res
