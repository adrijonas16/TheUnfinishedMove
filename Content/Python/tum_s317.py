# War readability: brighter dusk, lower walls so the battle is visible, duels inside the field edges
import unreal, random, math, importlib
import tum_s195 as W; importlib.reload(W)
E = W.E; L = W.L; V = unreal.Vector
def run():
    L.load_level("/Game/TUM/Maps/M_Cut_WarField")
    out = {"walls": 0}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label(); f = str(a.get_folder_path())
        if isinstance(a, unreal.StaticMeshActor) and (f.startswith("Art/War/LaneWalls") or lab.startswith("Ruin_")):
            o, e = a.get_actor_bounds(False); cap = 150.0 if f.startswith("Art/War/LaneWalls") else 230.0
            if 2 * e.z > cap:
                s = a.get_actor_scale3d(); k = cap / (2 * e.z); a.set_actor_scale3d(V(s.x, s.y, s.z * k))
                o2, e2 = a.get_actor_bounds(False); l = a.get_actor_location(); a.set_actor_location(V(l.x, l.y, l.z + (o.z - e.z) - (o2.z - e2.z)), False, False)
                out["walls"] += 1
        if lab == "Sun":
            a.set_actor_rotation(unreal.Rotator(roll=0, pitch=-16, yaw=150), False); a.light_component.set_intensity(9.0)
        if isinstance(a, unreal.PostProcessVolume):
            s = a.settings; s.set_editor_property("override_auto_exposure_bias", True); s.set_editor_property("auto_exposure_bias", 2.2); a.settings = s
        if isinstance(a, unreal.SkyLight): a.light_component.set_intensity(2.0); a.light_component.recapture_sky()
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Duel_Edge_"): E.destroy_actor(a)
    random.seed(9); n = 0
    for side in (-1, 1):
        for x in (900, 1900, 2800, 3900, 4800):
            x += random.uniform(-150, 150); y = side * random.uniform(2050, 2200); yaw = random.uniform(0, 360)
            dx, dy = math.cos(math.radians(yaw)) * 85, math.sin(math.radians(yaw)) * 85
            a = W.soldier(f"Duel_Edge_{n}a", x - dx, y - dy, 4, yaw - 90, random.choice(W.FIGHT), skin=W.SKINS[1], pos=random.uniform(0, 1))
            b = W.soldier(f"Duel_Edge_{n}b", x + dx, y + dy, 4, yaw + 90, random.choice(W.DEF + W.FIGHT), skin=W.SKINS[3], pos=random.uniform(0, 1))
            n += 1
    out["duels"] = n
    L.save_current_level(); return out
