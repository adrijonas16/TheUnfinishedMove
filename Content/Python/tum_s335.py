# Checkpoints (lantern post, soft light) + on-screen route map in every cut; War crowd: nobody runs through solids, more varied soldiers; darker factory
import unreal, importlib, traceback, math, random
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; PH = f"{R}/Props/PolyHaven"; MAT = f"{R}/Materials/UI"
MOV = unreal.ComponentMobility.MOVABLE
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def world(): return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def ground_z(x, y, z0=3000.0, z1=-5000.0, ignore=()):
    h = unreal.SystemLibrary.line_trace_single(world(), V(x, y, z0), V(x, y, z1), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, list(ignore), unreal.DrawDebugTrace.NONE, True)
    if h: 
        t = h.to_tuple(); return t[4].z if hasattr(t[4], "z") else None
    return None
def sma(mesh, name, loc, rot=(0, 0, 0), scale=1.0, folder="Gameplay/Checkpoint", collide=False, tags=()):
    a = E.spawn_actor_from_class(unreal.StaticMeshActor, V(*loc), unreal.Rotator(roll=rot[2], pitch=rot[1], yaw=rot[0]))
    c = a.static_mesh_component; c.set_mobility(MOV); c.set_static_mesh(EAL.load_asset(mesh) if isinstance(mesh, str) else mesh)
    a.set_actor_scale3d(V(scale, scale, scale) if not isinstance(scale, tuple) else V(*scale))
    if not collide: c.set_collision_profile_name("NoCollision"); a.set_actor_enable_collision(False)
    a.set_actor_label(name); a.set_folder_path(folder); a.tags = list(tags); return a
def height(mesh):
    b = EAL.load_asset(mesh).get_bounding_box(); return b.max.z - b.min.z, b
def clear(prefixes):
    n = 0
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(prefixes): E.destroy_actor(a); n += 1
    return n

POLE = "/Game/MS/3D/Old_Wooden_Pole_ueqfdi0ga/SM_Old_Wooden_Pole_ueqfdi0ga_01_N1"
LANT = [f"{PH}/Lantern_01/Lantern_01/StaticMeshes/Lantern_01", f"{PH}/Lantern_01/Lantern_01/StaticMeshes/Lantern_01_glass"]
ROCKS = [f"{PH}/rock_moss_set_01/rock_moss_set_01/StaticMeshes/rock_moss_set_01_rock0{i}" for i in range(1, 7)]
def checkpoint(name, x, y, tags, z=None, pole_h=300.0, light=1600.0, folder="Gameplay/Checkpoint"):
    if z is None: z = ground_z(x, y)
    if z is None: z = 0.0
    ph, pb = height(POLE); s = pole_h / max(ph, 1.0)
    sma(POLE, f"{name}_Pole", (x, y, z - pb.min.z * s), scale=s, folder=folder, collide=True)
    lh, lb = height(LANT[0]); ls = 42.0 / max(lh, 1.0); top = z + pole_h
    for i, m in enumerate(LANT): sma(m, f"{name}_Lantern{i}", (x, y, top - lb.min.z * ls), scale=ls, folder=folder)
    random.seed(hash(name) & 0xffff)
    for i in range(4):
        a = random.uniform(0, 6.28); r = random.uniform(45, 80)
        sma(random.choice(ROCKS), f"{name}_Rock{i}", (x + math.cos(a) * r, y + math.sin(a) * r, z - 4), rot=(random.uniform(0, 360), 0, 0), scale=random.uniform(0.35, 0.6), folder=folder)
    l = E.spawn_actor_from_class(unreal.PointLight, V(x, y, top + 25), unreal.Rotator())
    lc = l.point_light_component; lc.set_intensity(light); lc.set_light_color(unreal.LinearColor(1.0, 0.58, 0.24, 1)); lc.set_attenuation_radius(900.0); lc.set_cast_shadows(False)
    l.set_actor_label(f"{name}_Light"); l.set_folder_path(folder)
    t = E.spawn_actor_from_class(unreal.TargetPoint, V(x, y, z + 100), unreal.Rotator()); t.tags = list(tags); t.set_actor_label(f"{name}_Goal"); t.set_folder_path(folder)
    return round(z)

def map_actors():
    clear(("Map_",))
    def m(shape, mi, tag):
        a = E.spawn_actor_from_class(unreal.StaticMeshActor, V(0, 0, -9000), unreal.Rotator())
        c = a.static_mesh_component; c.set_mobility(MOV); c.set_static_mesh(EAL.load_asset(f"/Engine/BasicShapes/{shape}"))
        c.set_material(0, EAL.load_asset(f"{MAT}/MI_Map_{mi}")); c.set_collision_profile_name("NoCollision"); c.set_cast_shadow(False); a.set_actor_enable_collision(False)
        try: c.set_editor_property("translucency_sort_priority", {"Bar": 0, "Track": 1, "Goal": 2, "You": 3}[mi])
        except Exception: pass
        a.tags = [tag]; a.set_actor_label(f"Map_{tag}"); a.set_folder_path("UI/Map")
    m("Cube", "Bar", "MapBar"); m("Cube", "Track", "MapTrack"); m("Sphere", "Track", "MapStart"); m("Sphere", "Goal", "MapGoal"); m("Sphere", "You", "MapYou")
    t = E.spawn_actor_from_class(unreal.TextRenderActor, V(0, 0, -9000), unreal.Rotator()); t.root_component.set_mobility(MOV)
    tc = t.text_render; tc.set_text(unreal.Text("CHECKPOINT")); tc.set_world_size(1.0)
    tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER); tc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_BOTTOM)
    tc.set_text_render_color(unreal.Color(r=255, g=170, b=90, a=255)); tc.set_cast_shadow(False)
    try: tc.set_text_material(EAL.load_asset(f"{R}/Materials/M_TextGlow"))
    except Exception: pass
    t.tags = ["MapLabel"]; t.set_actor_label("Map_Label"); t.set_folder_path("UI/Map")
    return "ok"

def light_scale(prefix_mult):
    out = {}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        for pre, val in prefix_mult.items():
            if lab.startswith(pre) and isinstance(a, unreal.Light):
                lc = a.get_component_by_class(unreal.LightComponent)
                new = val if val > 50 else lc.intensity * val
                lc.set_intensity(new); out[lab] = round(new)
    return out

# ---------------- War ----------------
SOLID_SKIP = ("GroundTile", "War_Ground", "Floor", "End_Floor", "Kill", "Map_", "Trench_Planks", "Debris", "CP_", "Sky", "Fog")
def obstacles():
    obs = []
    for a in E.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor): continue
        lab = a.get_actor_label()
        if lab.startswith(SOLID_SKIP) or a.is_hidden_ed(): continue
        o, e = a.get_actor_bounds(False)
        if e.z < 35 or (o.z - e.z) > 160 or e.x > 2600 or e.y > 2600 or e.x < 12 or e.y < 12: continue
        obs.append((a, o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y))
    return obs
def inside(x, y, b, pad): return b[1] - pad < x < b[2] + pad and b[3] - pad < y < b[4] + pad
def first_hit(x, y, dx, dy, dist, obs, pad=70.0):
    s = 0.0
    while s < dist:
        px, py = x + dx * s, y + dy * s
        for b in obs:
            if inside(px, py, b, pad): return s
        s += 40.0
    return None
def war():
    out = {}
    obs = obstacles(); out["obstacles"] = len(obs)
    nb = 0
    for b in obs:
        c = b[0].static_mesh_component
        if c.get_collision_profile_name() == "NoCollision" or not b[0].get_actor_enable_collision():
            c.set_collision_profile_name("BlockAll"); b[0].set_actor_enable_collision(True); nb += 1
    out["made_solid"] = nb
    acts = {a.get_actor_label(): a for a in E.get_all_level_actors()}
    removed, shortened = [], 0
    for lab, a in list(acts.items()):
        if lab.startswith("Runner_") and not lab.endswith("_Mesh"):
            l = a.get_actor_location(); f = a.get_actor_forward_vector(); d = a.get_editor_property("Dist")
            s = first_hit(l.x, l.y, f.x, f.y, d, obs)
            if s is not None and s < 500:
                removed.append(lab); E.destroy_actor(a)
                if f"{lab}_Mesh" in acts: E.destroy_actor(acts[f"{lab}_Mesh"])
            elif s is not None: a.set_editor_property("Dist", float(s - 60)); shortened += 1
        if lab.startswith("DuelPair_"):
            bad = False
            for k in ("A", "B"):
                m = a.get_editor_property(k)
                if m:
                    ml = m.get_actor_location()
                    if any(inside(ml.x, ml.y, b, 55) for b in obs): bad = True
            if bad:
                for k in ("A", "B"):
                    m = a.get_editor_property(k)
                    if m: E.destroy_actor(m)
                removed.append(lab); E.destroy_actor(a)
        if lab.startswith("Hunter_") and not lab.endswith("_Mesh"):
            l = a.get_actor_location()
            if any(inside(l.x, l.y, b, 80) for b in obs): out.setdefault("hunter_inside", []).append(lab)
    out["removed"] = removed; out["shortened"] = shortened
    # variety: size, build and skin spread; no two neighbours identical
    import tum_s195 as W
    random.seed(4242); n = 0
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.SkeletalMeshActor) and a.get_actor_label().startswith(("Runner_", "Duel", "Hunter_", "Crowd_")):
            c = a.skeletal_mesh_component
            if not a.get_actor_label().startswith("Hunter_"):
                try: c.set_skeletal_mesh_asset(EAL.load_asset(random.choice(W.SKINS)))
                except Exception: pass
            s = random.uniform(0.86, 1.12); w = random.uniform(0.94, 1.08)
            a.set_actor_scale3d(V(s * w, s * w, s)); n += 1
    out["varied"] = n
    # tame the shrine light, add the checkpoint
    out["lights"] = light_scale({"Shrine_Light": 2500.0})
    clear(("CP_War",))
    out["cp"] = checkpoint("CP_War", 5650, -330, ["Goal"])
    out["map"] = map_actors()
    # fire template for the dragon beacon
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith("Fire") and not isinstance(a, unreal.Light):
            for cc in (unreal.NiagaraComponent, unreal.ParticleSystemComponent):
                comp = a.get_component_by_class(cc)
                if comp:
                    tpl = comp.get_asset() if cc == unreal.NiagaraComponent else comp.get_editor_property("template")
                    if tpl: out["fire"] = tpl.get_path_name(); break
            if "fire" in out: break
    return out

def factory():
    out = {"lights": light_scale({"Spine_Light_": 0.3, "WindowLight_": 2500.0, "Chess_Lamp": 4000.0, "Story_Light": 3000.0, "City_Light_": 6000.0, "Goal_Glow": 0.2})}
    clear(("CP_F",))
    pts = {0: (3500, 140), 1: (5450, -420), 2: (6450, -430), 3: (8300, 160)}
    out["cp"] = {n: checkpoint(f"CP_F{n}", x, y, [f"GoalS{n}"], pole_h=260.0, light=1100.0) for n, (x, y) in pts.items()}
    out["map"] = map_actors(); return out

def dragon(fire):
    out = {}
    clear(("CP_Dragon", "Beacon_"))
    stack = None
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith("SeaStack_") and isinstance(a, unreal.StaticMeshActor): stack = a; break
    gx, gy, top = 12900.0, 0.0, 1650.0
    if stack:
        m = stack.static_mesh_component.static_mesh; bb = m.get_bounding_box(); h = bb.max.z - bb.min.z
        sz = (top + 2200.0) / h
        a = sma(m, "Beacon_Stack", (gx, gy, -2200.0 - bb.min.z * sz), rot=(35, 0, 0), scale=(sz * 0.55, sz * 0.55, sz), folder="Art/Dragon/Beacon", collide=True)
        o, e = a.get_actor_bounds(False); top = o.z + e.z; out["stack"] = [m.get_name(), round(top)]
    out["cp"] = checkpoint("CP_Dragon", gx, gy, ["Goal"], z=top, pole_h=420.0, light=9000.0, folder="Art/Dragon/Beacon")
    if fire:
        fa = E.spawn_actor_from_class(unreal.Actor, V(gx, gy, top + 430), unreal.Rotator())
        t = EAL.load_asset(fire)
        if isinstance(t, unreal.NiagaraSystem):
            fa = unreal.NiagaraActor and E.spawn_actor_from_object(t, V(gx, gy, top + 440), unreal.Rotator())
        else:
            fa = E.spawn_actor_from_object(t, V(gx, gy, top + 440), unreal.Rotator())
        if fa: fa.set_actor_scale3d(V(2.5, 2.5, 2.5)); fa.set_actor_label("Beacon_Fire"); fa.set_folder_path("Art/Dragon/Beacon")
    out["lights"] = light_scale({"CurrentLight_": 0.5})
    out["map"] = map_actors(); return out

def cliff():
    out = {"lights": light_scale({"Arch_Light": 3000.0})}
    clear(("CP_Cliff",)); out["cp"] = checkpoint("CP_Cliff", 5500, 260, ["Goal"])
    out["map"] = map_actors(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField"); step("war", war); L.save_current_level()
    fire = res.get("war", {}).get("fire") if isinstance(res.get("war"), dict) else None
    L.load_level(f"{R}/Maps/M_Cut_Dragon"); step("dragon", lambda: dragon(fire)); L.save_current_level()
    L.load_level(f"{R}/Maps/M_Cut_Cliff"); step("cliff", cliff); L.save_current_level()
    L.load_level(f"{R}/Maps/M_FactoryHub"); step("factory", factory); L.save_current_level()
    return res
