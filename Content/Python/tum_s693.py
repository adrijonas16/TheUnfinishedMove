# Dragon world v3: a canyon WITH a floor. River 20 m under the flight path, single-tier walls that grow out of the water
# (nothing can float), every wall piece turned so its solid face looks at the flight path (ray-tested), rock spurs chosen
# for least stretching, start ledge raised onto the canyon wall. Gameplay x/y coordinates unchanged.
import unreal, math, random, traceback
import tum_s291 as D
import tum_s679 as W
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; MS = "/Game/MS/3D"; SKY = "/Game/TUM/Materials/Sky"; SEA = 0.0; LIFT = 2400.0
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def river_mat():
    p = f"{SKY}/M_River"
    if EAL.does_asset_exist(p): return EAL.load_asset(p)
    m = AT.create_asset("M_River", SKY, unreal.Material, unreal.MaterialFactoryNew()); ex, con = D.ex, D.con
    wp = ex(m, unreal.MaterialExpressionWorldPosition, -1200, 0); xy = ex(m, unreal.MaterialExpressionComponentMask, -1050, 0, r=True, g=True); con(wp, "", xy, "")
    d = ex(m, unreal.MaterialExpressionDivide, -900, 0, const_b=1800.0); con(xy, "", d, "A")
    pn = ex(m, unreal.MaterialExpressionPanner, -750, 0, speed_x=0.035, speed_y=0.004); con(d, "", pn, "Coordinate")
    t = ex(m, unreal.MaterialExpressionTextureSample, -550, 0, texture=EAL.load_asset("/Engine/EngineSky/T_Sky_Clouds_M")); con(pn, "", t, "UVs")
    r = ex(m, unreal.MaterialExpressionComponentMask, -350, 0, r=True); con(t, "RGB", r, "")
    c1 = ex(m, unreal.MaterialExpressionConstant3Vector, -350, -250, constant=unreal.LinearColor(0.012, 0.075, 0.085, 1))
    c2 = ex(m, unreal.MaterialExpressionConstant3Vector, -350, -120, constant=unreal.LinearColor(0.10, 0.26, 0.27, 1))
    lp = ex(m, unreal.MaterialExpressionLinearInterpolate, -150, -150); con(c1, "", lp, "A"); con(c2, "", lp, "B"); con(r, "", lp, "Alpha")
    MEL.connect_material_property(lp, "", unreal.MaterialProperty.MP_BASE_COLOR)
    ro = ex(m, unreal.MaterialExpressionConstant, -150, 100, r=0.08); MEL.connect_material_property(ro, "", unreal.MaterialProperty.MP_ROUGHNESS)
    sp = ex(m, unreal.MaterialExpressionConstant, -150, 180, r=0.9); MEL.connect_material_property(sp, "", unreal.MaterialProperty.MP_SPECULAR)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return m
def world():
    random.seed(4040); world_ = unreal.EditorLevelLibrary.get_editor_world()
    kill_folders = ("Art/Dragon/World", "Art/Dragon/Spires", "Art/Dragon/Gates", "Art/Dragon/Peaks", "Art/Dragon/Canyon", "Dragon/Sky")
    keep = ("Sea_Plane", "Start_Floor", "Kill_Floor", "Start_Top", "Start_Arch", "Start_Col_0", "Start_Wall_0", "Start_Tree")
    out = {"deleted": 0}
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label(); f = str(a.get_folder_path())
        if (f.startswith(kill_folders) and lab not in keep) or lab in ("CP_Dragon_Pole", "Beacon_Stack") or lab.startswith("ShotCam"): E.destroy_actor(a); out["deleted"] += 1
    # raise the start onto the canyon wall (only once)
    ps = [a for a in E.get_all_level_actors() if isinstance(a, unreal.PlayerStart)][0]
    if ps.get_actor_location().z < 0:
        for a in E.get_all_level_actors():
            if a is ps or a.get_actor_label() in ("Start_Floor", "Start_Top", "Start_Arch", "Start_Col_0", "Start_Wall_0", "Start_Tree", "Dragon_Mesh", "Hint_Boost"):
                l = a.get_actor_location(); a.set_actor_location(V(l.x, l.y, l.z + LIFT), False, False)
        out["lifted"] = True
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "Sea_Plane":
            l = a.get_actor_location(); a.set_actor_location(V(l.x, l.y, SEA), False, False); a.static_mesh_component.set_material(0, river_mat())
        if isinstance(a, unreal.ExponentialHeightFog):
            a.set_actor_location(V(0, 0, SEA), False, False); fc = a.get_editor_property("component"); fc.set_editor_property("fog_density", 0.012); fc.set_editor_property("fog_height_falloff", 0.02)
    massive = D.sms(f"{MS}/Massive_Nordic_Coastal_Cliff_ullqbb1ga") + D.sms(f"{MS}/Massive_Nordic_Coastal_Cliff_vdssailfa") + D.sms(f"{MS}/Massive_Nordic_Coastal_Cliff_vefkehbva") + D.sms(f"{MS}/Massive_Nordic_Coastal_Cliff_veqnci0db")
    huge = D.sms(f"{MS}/Huge_Nordic_Coastal_Cliff_ulkiejkva") + D.sms(f"{MS}/Huge_Nordic_Coastal_Cliff_venrdcgga") + D.sms(f"{MS}/Nordic_Coastal_Cliff_ulmiccava")
    stacks = D.sms(f"{MS}/Nordic_Beach_Rock_Formation_vd4iecjva") + D.sms(f"{MS}/Nordic_Beach_Rock_Formation_vckqccbga") + D.sms(f"{MS}/Nordic_Beach_Rock_Formation_vfgkajyga")
    cliffs = massive + huge; F = "Art/Dragon/Canyon"
    def coverage(a, x, side, w, top):
        a.set_actor_enable_collision(True); hits = 0; n = 0
        for xi in (x - 0.28 * w, x, x + 0.28 * w):
            for zi in (300.0, 900.0, 1500.0, 2100.0, min(2700.0, top - 150)):
                n += 1
                r = unreal.SystemLibrary.line_trace_single(world_, V(xi, side * 150, zi), V(xi, side * 7000, zi), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
                t = r.to_tuple() if r else None
                if t and t[0] and t[9] == a and abs(t[4].y) < 3200: hits += 1
        a.set_actor_enable_collision(False); return hits / n
    def wall(name, x, side, top, w, margin):
        mesh = random.choice(cliffs); best = None; y0 = random.uniform(0, 90)
        for k in range(4):
            a = D.place(mesh, name, x, side * 3000, top, top - (SEA - 400), y0 + k * 90, F, w=w)
            o, e = a.get_actor_bounds(False); inner = o.y - side * e.y; l = a.get_actor_location()
            a.set_actor_location(V(l.x, l.y + side * (1125 + margin) - inner, l.z), False, False)
            c = coverage(a, x, side, w, top)
            if best is None or c > best[1]:
                if best: E.destroy_actor(best[0])
                best = (a, c)
            else: E.destroy_actor(a)
            if best[1] > 0.93: break
        return best[1]
    covs = []; n = 0
    for side in (-1, 1):
        x = -10800.0
        while x < 16800:
            covs.append(round(wall(f"Wall_{n}", x, side, random.uniform(2300, 3400), random.uniform(3600, 4600), random.uniform(80, 450)), 2)); n += 1
            x += random.uniform(1300, 1700)
    out["walls"] = n; out["coverage_min_avg"] = [min(covs), round(sum(covs) / len(covs), 2)]; out["low_cov"] = sum(1 for c in covs if c < 0.6)
    for i in range(16):
        side = -1 if i % 2 else 1; top = random.uniform(5500, 9500)
        D.place(random.choice(massive), f"Rim_{i}", -11000 + i * 1900 + random.uniform(-600, 600), side * random.uniform(5500, 8000), top, top + 400, random.uniform(0, 360), F, w=random.uniform(6500, 9500))
    for i in range(18):
        ang = i / 18 * 2 * math.pi + random.uniform(-0.12, 0.12); rad = random.uniform(17000, 26000); top = random.uniform(8000, 15000)
        D.place(random.choice(massive), f"Horizon_{i}", 3000 + math.cos(ang) * rad, math.sin(ang) * rad * 0.85, top, top + 400, random.uniform(0, 360), F, w=random.uniform(11000, 17000))
    for i, (x, y, top) in enumerate(((21000, -2500, 14500), (23500, 4200, 11500), (18500, 6500, 9000), (19500, -7000, 10000))):
        D.place(massive[i % len(massive)], f"Ahead_{i}", x, y, top, top + 400, random.uniform(0, 360), F, w=13000)
    D.place(massive[0], "Back_Wall", -12400, 0, 4200, 4600, 20, F, w=7500)
    D.place(massive[0], "Start_Cliff", -8500, 0, 1000 - 15, 1400, 30, F, w=3300)
    for i in range(34):   # shore rocks at the foot of the walls + a few in the channel
        side = random.choice((-1, 1)); x = random.uniform(-9500, 15500); y = side * random.uniform(700, 1250) if i < 26 else random.uniform(-500, 500); top = random.uniform(120, 650)
        D.place(random.choice(stacks), f"Shore_{i}", x, y, top, top + 300, random.uniform(0, 360), F, w=random.uniform(450, 900))
    # spurs (obstacles): least-distorted mesh for the box, growing from the water out of the wall
    cands = huge + stacks; nat = {}
    for m in cands:
        t = E.spawn_actor_from_object(m, V(0, 0, -50000), unreal.Rotator()); o, e = t.get_actor_bounds(False); nat[m.get_name()] = (max(e.x, 1), max(e.y, 1), max(e.z, 1)); E.destroy_actor(t)
    spurs = 0; dist = []
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith("StormWall_"):
            o, e = a.get_actor_bounds(False); side = 1 if o.y > 0 else -1
            inner = o.y - side * e.y; outer = side * 2300.0; cy = (inner + outer) / 2; ly = abs(outer - inner); bx, bz = 2 * e.x + 60, 3400.0 + 300
            best = None
            for m in cands:
                ex0, ey0, ez0 = nat[m.get_name()]
                for yaw in (0, 90):
                    s = (ly / (2 * ex0), bx / (2 * ey0), bz / (2 * ez0)) if yaw == 90 else (bx / (2 * ex0), ly / (2 * ey0), bz / (2 * ez0))
                    r = max(s) / min(s)
                    if best is None or r < best[0]: best = (r, m, yaw)
            W.fit(best[1], f"Spur_{spurs}", o.x, cy, SEA - 300, 3400, bx, ly, best[2], F); dist.append(round(best[0], 2)); spurs += 1
    out["spurs"] = spurs; out["spur_distortion"] = dist
    fire = None
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "Beacon_Fire": fire = a.niagara_component.get_asset()
    for i, gx in enumerate((4030, 7530, 10530)):
        for side in (-1, 1):
            top = random.uniform(2450, 2750)
            D.place(random.choice(stacks), f"GatePillar_{i}_{side}", gx, side * 1800, top, top - SEA + 300, random.uniform(0, 360), F, w=1250)
            if fire:
                fa = E.spawn_actor_from_object(fire, V(gx, side * 1800, top + 40)); fa.set_actor_scale3d(V(1.6, 1.6, 1.6)); fa.set_actor_label(f"GateFire_{i}_{side}"); fa.set_folder_path(F)
    D.place(stacks[0], "Beacon_Stack", 12900, 0, 1650, 1650 - SEA + 300, 15, "Art/Dragon/Beacon", w=1500)
    L.save_current_level(); return out
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon"); step("world", world); return res
