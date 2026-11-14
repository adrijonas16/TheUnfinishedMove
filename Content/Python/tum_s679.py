# Dragon world rebuild: a deep fjord canyon. Nothing floats: canyon walls in two tiers rise from the sea on both sides of the
# flight path, obstacles are rock spurs growing out of the walls, the "boost" gates are natural rock bridges from wall to
# wall, mountains ring the horizon. Gameplay coordinates (route, bounds, gates) are unchanged.
import unreal, math, random, traceback, importlib
import tum_s291 as D
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; MS = "/Game/MS/3D"; SEA = -2600.0
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def fit(mesh, name, cx, cy, zb, zt, sx_, sy_, yaw, folder):
    a = E.spawn_actor_from_object(mesh, V(0, 0, 0), unreal.Rotator())
    o, e = a.get_actor_bounds(False); ex0, ey0, ez0 = max(e.x, 1), max(e.y, 1), max(e.z, 1)
    if yaw in (90, 270): sc = V(sy_ / (2 * ex0), sx_ / (2 * ey0), (zt - zb) / (2 * ez0))
    else: sc = V(sx_ / (2 * ex0), sy_ / (2 * ey0), (zt - zb) / (2 * ez0))
    a.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=yaw), False); a.set_actor_scale3d(sc)
    o, e = a.get_actor_bounds(False); l = a.get_actor_location()
    a.set_actor_location(V(l.x + cx - o.x, l.y + cy - o.y, l.z + (zb + zt) / 2 - o.z), False, False)
    a.set_actor_enable_collision(False); a.set_actor_label(name); a.set_folder_path(folder); return a
def world():
    random.seed(2026)
    kill_folders = ("Art/Dragon/World", "Art/Dragon/Spires", "Art/Dragon/Gates", "Art/Dragon/Peaks", "Art/Dragon/Canyon", "Dragon/Sky")
    keep = ("Sea_Plane", "Start_Floor", "Kill_Floor", "Start_Top", "Start_Arch", "Start_Col_0", "Start_Wall_0", "Start_Tree")
    n_del = 0
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label(); f = str(a.get_folder_path())
        if (f.startswith(kill_folders) and lab not in keep) or (lab.startswith("Current_") and isinstance(a, unreal.StaticMeshActor)) or lab in ("CP_Dragon_Pole", "Beacon_Stack"):
            E.destroy_actor(a); n_del += 1
    massive = D.sms(f"{MS}/Massive_Nordic_Coastal_Cliff_ullqbb1ga") + D.sms(f"{MS}/Massive_Nordic_Coastal_Cliff_vdssailfa") + D.sms(f"{MS}/Massive_Nordic_Coastal_Cliff_vefkehbva") + D.sms(f"{MS}/Massive_Nordic_Coastal_Cliff_veqnci0db")
    huge = D.sms(f"{MS}/Huge_Nordic_Coastal_Cliff_ulkiejkva") + D.sms(f"{MS}/Huge_Nordic_Coastal_Cliff_venrdcgga") + D.sms(f"{MS}/Nordic_Coastal_Cliff_ulmiccava")
    stacks = D.sms(f"{MS}/Nordic_Beach_Rock_Formation_vd4iecjva") + D.sms(f"{MS}/Nordic_Beach_Rock_Formation_vckqccbga") + D.sms(f"{MS}/Nordic_Beach_Rock_Formation_vfgkajyga")
    cliffs = massive + huge; F = "Art/Dragon/Canyon"; out = {"deleted": n_del, "meshes": [len(massive), len(huge), len(stacks)]}
    def wall(name, x, side, top, bottom, w, margin):
        a = D.place(random.choice(cliffs), name, x, side * 3000, top, top - bottom, random.uniform(0, 360), F, w=w)
        o, e = a.get_actor_bounds(False); inner = o.y - side * e.y; l = a.get_actor_location()
        a.set_actor_location(V(l.x, l.y + side * (1125 + margin) - inner, l.z), False, False); return a
    n = 0
    for side in (-1, 1):
        x = -10500.0
        while x < 16500:
            wall(f"WallLow_{n}", x + random.uniform(-300, 300), side, random.uniform(500, 1500), SEA - 400, random.uniform(4200, 5200), random.uniform(60, 260))
            wall(f"WallHigh_{n}", x + random.uniform(-500, 500), side, random.uniform(3500, 4700), 200, random.uniform(4200, 5400), random.uniform(180, 650)); n += 1
            x += random.uniform(1500, 2000)
    out["walls"] = n * 2
    # second row: taller mountains right behind the canyon rim
    for i in range(16):
        side = -1 if i % 2 else 1; x = -11000 + i * 1900 + random.uniform(-600, 600)
        top = random.uniform(5500, 9500)
        D.place(random.choice(massive), f"Rim_{i}", x, side * random.uniform(5500, 8000), top, top + 3200, random.uniform(0, 360), F, w=random.uniform(6500, 9500))
    # horizon ring + the peaks you fly towards
    for i in range(18):
        ang = i / 18 * 2 * math.pi + random.uniform(-0.12, 0.12); rad = random.uniform(17000, 26000)
        x, y = 3000 + math.cos(ang) * rad, math.sin(ang) * rad * 0.85; top = random.uniform(8000, 15000)
        D.place(random.choice(massive), f"Horizon_{i}", x, y, top, top + 3400, random.uniform(0, 360), F, w=random.uniform(11000, 17000))
    for i, (x, y, top) in enumerate(((21000, -2500, 14500), (23500, 4200, 11500), (18500, 6500, 9000), (19500, -7000, 10000))):
        D.place(massive[i % len(massive)], f"Ahead_{i}", x, y, top, top + 3400, random.uniform(0, 360), F, w=13000)
    # closed end behind the take-off ledge
    D.place(massive[0], "Back_Low", -12200, 0, 1200, 1200 - SEA + 400, 20, F, w=7000); D.place(massive[1 % len(massive)], "Back_High", -12600, 300, 5200, 5000, 200, F, w=8000)
    # take-off ledge: a real cliff under the start floor
    D.place(massive[0], "Start_Cliff", -8500, 0, -1415, 1700, 30, F, w=3300)
    # small sea stacks far below, for depth
    for i in range(12):
        x = random.uniform(-6500, 15000); y = random.uniform(-900, 900); top = random.uniform(-2200, -900)
        D.place(random.choice(stacks), f"SeaStack_{i}", x, y, top, top - SEA + 200, random.uniform(0, 360), F, w=random.uniform(500, 1000))
    # obstacles = rock spurs growing out of the canyon wall; blockers resized to match
    spurs = 0
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("StormWall_"):
            o, e = a.get_actor_bounds(False); s = a.get_actor_scale3d()
            a.set_actor_scale3d(V(s.x * 380.0 / max(e.x, 1), s.y, s.z)); o, e = a.get_actor_bounds(False)
            side = 1 if o.y > 0 else -1
            inner = o.y - side * e.y; outer = side * 2300.0; cy = (inner + outer) / 2; ly = abs(outer - inner)
            m = random.choice(huge + stacks)
            fit(m, f"Spur_{spurs}_Hi", o.x, cy, 500, 3500, 820, ly, random.choice((0, 180)), F)
            fit(random.choice(huge + stacks), f"Spur_{spurs}_Lo", o.x, cy + side * 300, SEA - 300, 900, 1100, ly, random.choice((0, 180)), F); spurs += 1
    out["spurs"] = spurs
    # boost gates = natural rock bridges from wall to wall, above the flight path
    for i, gx in enumerate((4030, 7530, 10530)):
        fit(random.choice(huge), f"Bridge_{i}", gx, 0, 2920, 3650, 900, 4200, random.choice((0, 180)), F)
        for side in (-1, 1):
            fit(random.choice(stacks), f"Bridge_{i}_Leg{side}", gx, side * 1650, 400, 3200, 900, 1000, random.choice((0, 90, 180, 270)), F)
    # goal: a sea stack that reaches up to the beacon fire
    D.place(stacks[0], "Beacon_Stack", 12900, 0, 1650, 1650 - SEA + 300, 15, "Art/Dragon/Beacon", w=1700)
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.ExponentialHeightFog):
            fc = a.get_editor_property("component"); fc.set_editor_property("fog_density", 0.012); fc.set_editor_property("fog_height_falloff", 0.02)
    L.save_current_level(); return out
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon"); step("world", world); return res
