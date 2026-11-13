# War ground: real scanned rocky/cracked ground tiles instead of textured boxes, debris of battle, runners/duels never cross solid meshes, fairer hunters
import unreal, random, math, importlib, traceback
import tum_s195 as W; importlib.reload(W)
EAL = unreal.EditorAssetLibrary; E = W.E; L = W.L; V = unreal.Vector; MS = "/Game/MS/3D"; DC = "/Game/DerelictCorridor/Assets/Fab/Megascans/3D"
INV = "/Game/TUM/Materials/Surfaces/M_Invisible"
def sms(folder):
    return [EAL.load_asset(p) for p in EAL.list_assets(folder, False, False) if p.split("/")[-1].startswith("SM_")]
PITS = [(1500, 2100), (3000, 3600), (4400, 5000)]
def in_pit(x, y, r):
    return y + r > 830 and any(x0 - r < x < x1 + r for x0, x1 in PITS)
def tile(mesh, name, x, y, size, top, folder):
    a = E.spawn_actor_from_object(mesh, V(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360)))
    o, e = a.get_actor_bounds(False); s = size / max(2 * max(e.x, e.y), 1)
    a.set_actor_scale3d(V(s, s, s * random.uniform(0.6, 1.0)))
    o, e = a.get_actor_bounds(False); l = a.get_actor_location()
    a.set_actor_location(V(l.x + x - o.x, l.y + y - o.y, l.z + top - (o.z + e.z)), False, False)
    a.set_actor_enable_collision(False); a.static_mesh_component.set_cast_shadow(False)
    a.set_actor_label(name); a.set_folder_path(folder); return a
def run():
    L.load_level("/Game/TUM/Maps/M_Cut_WarField")
    out = {}
    for a in list(E.get_all_level_actors()):
        if str(a.get_folder_path()).startswith(("Art/War/GroundTiles", "Art/War/Debris")): E.destroy_actor(a)
    flat = [m for m in sms(f"{MS}/Nordic_Beach_Rocky_Ground_ukoncdamw") if "Flat" in m.get_name()] + sms(f"{MS}/Cracked_Nordic_Beach_Ground_vdymaajqx") + sms(f"{MS}/Nordic_Beach_Ground_vd4iahpga")
    rough = sms(f"{MS}/Rocky_Forest_Path_vefhef2ga") + sms(f"{MS}/Nordic_Beach_Rocky_Ground_ve3qdhmqx") + sms(f"{MS}/Nordic_Beach_Rocky_Ground_vf5pajccb")
    out["kinds"] = [m.get_name() for m in flat + rough]
    random.seed(77); n = 0
    # field: dense overlapping tiles whose top sits ~3 cm above the walkable floor
    x = -350
    while x < 6700:
        y = -2300
        while y < 2300:
            px, py = x + random.uniform(-120, 120), y + random.uniform(-120, 120)
            if not in_pit(px, py, 380):
                tile(random.choice(flat), f"GT_{n}", px, py, random.uniform(780, 1000), 3.0, "Art/War/GroundTiles"); n += 1
            y += 560
        x += 560
    # surroundings: bigger rough tiles out to the fog
    x = -9000
    while x < 16000:
        y = -14000
        while y < 14000:
            if not (-600 < x < 7000 and abs(y) < 2500):
                tile(random.choice(rough + flat), f"GTo_{n}", x + random.uniform(-400, 400), y + random.uniform(-400, 400), random.uniform(2200, 3000), -6.0, "Art/War/GroundTiles"); n += 1
            y += 1900
        x += 1900
    out["tiles"] = n
    # boxes become invisible collision; the plane catches falls
    for nme in ("Start_Floor", "End_Floor", "Floor_Cover", "Floor_Trench", "Mud_0", "Mud_1", "Mud_2", "Mud_3", "War_Ground"):
        a = W.find(nme)
        if a:
            m = EAL.load_asset(INV)
            for i in range(a.static_mesh_component.get_num_materials()): a.static_mesh_component.set_material(i, m)
    # pits read as dark mud water
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith("War_Pit_"): a.set_actor_location(V(a.get_actor_location().x, a.get_actor_location().y, -60), False, False)
    # battle debris: broken planks, swords, rubble, stakes, burnt trunks, barrels
    deb = []
    for f in (f"{DC}/Ind_Rubble_Debris_Plank_Wood_Broken_01", f"{DC}/Ind_Rubble_Debris_Concrete_Pack_01", f"{DC}/Forest_Scatter_Branch_Debris_04", f"{DC}/Forest_Scatter_Rock_Set_01", f"{MS}/Sword_uitlbiaga", f"{MS}/Wooden_Barrel_tmgmfeefa"):
        try: deb += sms(f)
        except Exception: pass
    k = 0
    for i in range(140):
        px, py = random.uniform(-200, 6500), random.uniform(-2200, 2200)
        if in_pit(px, py, 60) or abs(abs(py) - 800) < 70: continue
        m = random.choice(deb)
        a = E.spawn_actor_from_object(m, V(0, 0, 0), unreal.Rotator(roll=random.uniform(-8, 8), pitch=random.uniform(-8, 8), yaw=random.uniform(0, 360)))
        o, e = a.get_actor_bounds(False); big = max(e.x, e.y, e.z) * 2
        s = random.uniform(40, 120) / max(big, 1) if "Barrel" not in m.get_name() else 95 / max(2 * e.z, 1)
        a.set_actor_scale3d(V(s, s, s)); o, e = a.get_actor_bounds(False); l = a.get_actor_location()
        a.set_actor_location(V(l.x + px - o.x, l.y + py - o.y, l.z + 2 - (o.z - e.z) - 3), False, False)
        a.set_actor_enable_collision(False); a.set_actor_label(f"Debris_{k}"); a.set_folder_path("Art/War/Debris"); k += 1
    out["debris"] = k
    # solids that crowds must not cross
    solids = []
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor) and not a.get_editor_property("hidden"):
            f = str(a.get_folder_path())
            if f.startswith(("Art/War/GroundTiles", "Art/War/Debris")) or a.get_actor_label().startswith(("War_", "Sky_")): continue
            o, e = a.get_actor_bounds(False)
            if e.z > 60 and max(e.x, e.y) < 20000: solids.append((o.x - e.x - 60, o.x + e.x + 60, o.y - e.y - 60, o.y + e.y + 60))
    def hits(x0, y0, x1, y1):
        for (a0, a1, b0, b1) in solids:
            for t in range(0, 41):
                x = x0 + (x1 - x0) * t / 40; y = y0 + (y1 - y0) * t / 40
                if a0 < x < a1 and b0 < y < b1: return True
        return False
    rem = 0
    for r in [a for a in E.get_all_level_actors() if a.get_actor_label().startswith("Runner_") and not a.get_actor_label().endswith("_Mesh")]:
        l = r.get_actor_location(); f = r.get_actor_forward_vector(); t = r.get_editor_property("Traveled"); dist = r.get_editor_property("Dist")
        sx, sy = l.x - f.x * t, l.y - f.y * t
        if hits(sx, sy, sx + f.x * dist, sy + f.y * dist):
            for c in r.get_attached_actors(): E.destroy_actor(c)
            E.destroy_actor(r); rem += 1
    for d in [a for a in E.get_all_level_actors() if a.get_actor_label().startswith("DuelPair_")]:
        l = d.get_actor_location()
        if hits(l.x - 120, l.y, l.x + 120, l.y) or hits(l.x, l.y - 120, l.x, l.y + 120):
            for k_ in ("A", "B"):
                x = d.get_editor_property(k_)
                if x: E.destroy_actor(x)
            E.destroy_actor(d); rem += 1
    out["removed_crossing"] = rem
    # fairer hunters: shorter sight, a bit slower than the player
    for h in E.get_all_level_actors():
        if h.get_actor_label().startswith("Hunter_") and not h.get_actor_label().endswith("_Mesh"):
            h.set_editor_property("Sight", 720.0); h.set_editor_property("Speed", 360.0)
    L.save_current_level(); return out
