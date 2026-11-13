# Dragon + Cliff cuts: replace every graybox cube with real models (Fab Prowler dragon, Megascans cliffs/arches, volumetric clouds)
import unreal, random, math, traceback
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; MOV = unreal.ComponentMobility.MOVABLE; MS = "/Game/MS/3D"
PROW = "/Game/Fab/Prowler_Dragon_Variant_Rig/prowler_dragon_variant_rig/SkeletalMeshes"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1200:]
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a
def label(a, name, folder):
    a.set_actor_label(name); a.set_folder_path(folder); return a
def sm(p):
    m = EAL.load_asset(p)
    if not m: raise RuntimeError("missing " + p)
    return m
def first_sm(folder):
    return [p for p in EAL.list_assets(folder, False, False) if "/SM_" in p][0]
def hide_box(a, keep_collision=True):
    a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True)
    if not keep_collision: a.set_actor_enable_collision(False)
def fit(mesh, name, center, size, yaw=0.0, folder="Art", pitch=0.0, roll=0.0, uniform=False, collide=False):
    """Place mesh so its bounds fill the box (size = full extents x,y,z) in world axes (yaw 0/90 only for exactness)."""
    m = sm(mesh) if isinstance(mesh, str) else mesh
    b = m.get_bounding_box(); ext = b.max - b.min; mid = (b.max + b.min) * 0.5
    ex, ey = (ext.x, ext.y) if abs(math.sin(math.radians(yaw))) < 0.5 else (ext.y, ext.x)
    s = V(size[0] / max(ex, 1), size[1] / max(ey, 1), size[2] / max(ext.z, 1))
    if uniform: k = min(s.x, s.y, s.z); s = V(k, k, k)
    a = E.spawn_actor_from_object(m, V(0, 0, 0), unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw))
    a.set_actor_scale3d(s)
    o, e = a.get_actor_bounds(False)
    a.set_actor_location(V(center[0] - (o.x - 0), center[1] - (o.y - 0), center[2] - (o.z - 0)), False, False)
    if not collide: a.set_actor_enable_collision(False)
    return label(a, name, folder)
def clean(prefixes):
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(prefixes): E.destroy_actor(a)
def clouds(bottom_km=-0.2, thick_km=1.0):
    clean(("VolClouds",))
    c = E.spawn_actor_from_class(unreal.VolumetricCloud, V(0, 0, 0), unreal.Rotator())
    comp = c.get_component_by_class(unreal.VolumetricCloudComponent)
    comp.set_editor_property("layer_bottom_altitude", bottom_km); comp.set_editor_property("layer_height", thick_km)
    return label(c, "VolClouds", "Lighting")

# ------------------------------- DRAGON -------------------------------
def dragon():
    L.load_level("/Game/TUM/Maps/M_Cut_Dragon")
    clean(("Art_", "Dragon_Mesh", "Spire_", "Gate_", "Peak_"))
    # mount: Prowler dragon under the rider (tag DragonBody so BP_DragonRoute attaches it to the player)
    for n in ("Dragon_Body", "Dragon_Neck", "Dragon_Head", "Dragon_Tail", "Dragon_WingL", "Dragon_WingR"):
        a = find(n)
        if a: E.destroy_actor(a)
    d = E.spawn_actor_from_class(unreal.SkeletalMeshActor, V(0, 0, 1830), unreal.Rotator(roll=0, pitch=0, yaw=0))
    c = d.skeletal_mesh_component; c.set_mobility(MOV)
    mesh = EAL.load_asset(f"{PROW}/Object_36")
    try: c.set_skeletal_mesh_asset(mesh)
    except Exception: c.set_editor_property("skeletal_mesh_asset", mesh)
    c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    pd = unreal.SingleAnimationPlayData(); pd.set_editor_property("anim_to_play", EAL.load_asset(f"{PROW}/prowler_dragon_variant_rigAction_001"))
    pd.set_editor_property("saved_looping", True); pd.set_editor_property("saved_playing", True); c.set_editor_property("animation_data", pd)
    c.set_collision_profile_name("NoCollision"); d.set_actor_enable_collision(False)
    d.tags = ["DragonBody", "TUM_Built"]; label(d, "Dragon_Mesh", "Dragon/Mount")
    o, e = d.get_actor_bounds(False)
    k = 900.0 / max(2 * e.x, 2 * e.y, 1)   # ~9 m long/wide
    d.set_actor_scale3d(V(k, k, k))
    o, e = d.get_actor_bounds(False)
    d.set_actor_location(V(d.get_actor_location().x - o.x + 20, d.get_actor_location().y - o.y, d.get_actor_location().z + (1905 - (o.z + e.z * 0.55))), False, False)
    out = {"dragon_ext": [round(e.x), round(e.y), round(e.z)]}
    # invisible bounds
    for n in ("Bound_N", "Bound_S", "Bound_Low", "Bound_High", "Bound_Back"):
        a = find(n)
        if a: hide_box(a)
    # cloud sea -> real volumetric clouds below the flight
    cs = find("CloudSea")
    if cs: hide_box(cs, keep_collision=False)
    clouds(-0.25, 0.22)
    # storm walls -> jagged rock spires that fill the same collision volume
    spires = [first_sm(f"{MS}/Nordic_Beach_Rock_Formation_vd4iecjva"), first_sm(f"{MS}/Nordic_Beach_Rock_Formation_vckqccbga"), first_sm(f"{MS}/Icelandic_Rock_Assembly_tdbmcflda")]
    random.seed(3)
    for i, n in enumerate(("StormWall_0", "StormWall_1", "StormWall_2", "StormWall_3b")):
        a = find(n)
        if not a: continue
        o, e = a.get_actor_bounds(False); hide_box(a)
        fit(random.choice(spires), f"Spire_{i}", (o.x, o.y, o.z - 300), (e.x * 2.6, e.y * 2.15, e.z * 2 + 1600), yaw=random.choice((0, 180)), folder="Art/Dragon/Spires")
    # wind gates -> floating ruined stone arches the dragon flies through
    arch = first_sm(f"{MS}/Modular_Church_Ruin_Stone_Arch_02_xjurabvs")
    for g in range(3):
        parts = [find(f"Current_{g}_{s}") for s in ("Top", "Bot", "N", "S")]
        if not parts[0]: continue
        x = parts[0].get_actor_location().x
        for p in parts: hide_box(p, keep_collision=False)
        fit(arch, f"Gate_{g}", (x, 0, 2100), (300, 2500, 1700), yaw=90, folder="Art/Dragon/Gates")
        li = find(f"CurrentLight_{g}")
        if li: li.point_light_component.set_light_color(unreal.LinearColor(0.75, 0.85, 1.0, 1)); li.point_light_component.set_intensity(30000.0)
    # distant mountain peaks above the clouds
    cliffs = [first_sm(f"{MS}/Massive_Nordic_Coastal_Cliff_ullqbb1ga"), first_sm(f"{MS}/Massive_Nordic_Coastal_Cliff_vdssailfa"), first_sm(f"{MS}/Huge_Nordic_Coastal_Cliff_ulkiejkva")]
    for i, (x, y, h) in enumerate(((3000, 9000, 6500), (9000, -10000, 8000), (14000, 7000, 7000), (-4000, -7000, 5500), (20000, -2000, 9000), (6000, 16000, 9000))):
        fit(random.choice(cliffs), f"Peak_{i}", (x, y, h / 2 - 2500), (h * 0.9, h * 0.9, h), yaw=random.uniform(0, 360), uniform=True, folder="Art/Dragon/Peaks")
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "Sun":
            a.set_actor_rotation(unreal.Rotator(roll=0, pitch=-14, yaw=200), False); a.light_component.set_intensity(8.0)
            a.light_component.set_light_color(unreal.LinearColor(1.0, 0.78, 0.6, 1))
        if isinstance(a, unreal.SkyLight): a.light_component.recapture_sky()
    L.save_current_level(); return out

# ------------------------------- CLIFF -------------------------------
def cliff():
    L.load_level("/Game/TUM/Maps/M_Cut_Cliff")
    clean(("Ledge_", "CliffMass_", "Arch_Art", "Slab_", "Peak_", "Rock_"))
    rocky = [p for p in EAL.list_assets(f"{MS}/Nordic_Beach_Rocky_Ground_ukoncdamw", False, False) if "/SM_" in p and "Flat" in p]
    massive = [first_sm(f"{MS}/Massive_Nordic_Coastal_Cliff_ullqbb1ga"), first_sm(f"{MS}/Massive_Nordic_Coastal_Cliff_vefkehbva"), first_sm(f"{MS}/Quarry_Cliff_ub5tefsda")]
    random.seed(11)
    for n, tag in (("Start_Ledge", "S"), ("End_Ledge", "E")):
        a = find(n)
        if not a: continue
        o, e = a.get_actor_bounds(False); hide_box(a)
        # walking surface: flat rocky ground just above the collision top
        fit(rocky[0], f"Ledge_{tag}_Top", (o.x, o.y, o.z + e.z - 6), (e.x * 2.1, e.y * 2.1, 40), folder="Art/Cliff")
        # cliff mass falling away under it
        fit(random.choice(massive), f"CliffMass_{tag}", (o.x, o.y, o.z + e.z - 1700), (e.x * 2.6, e.y * 2.4, 3300), folder="Art/Cliff")
    w = find("Start_CliffWall")
    if w:
        o, e = w.get_actor_bounds(False); hide_box(w)
        fit(massive[0], "CliffMass_Wall", (o.x - 300, o.y, o.z + 200), (e.x * 2 + 900, e.y * 2.4, e.z * 2 + 1400), yaw=90, folder="Art/Cliff")
    m = find("Mist")
    if m: hide_box(m, keep_collision=False)
    clouds(-0.6, 0.35)
    # arch
    for n in ("Arch_Pillar_S", "Arch_Pillar_N", "Arch_Lintel"):
        a = find(n)
        if a: hide_box(a)
    fit(first_sm(f"{MS}/Modular_Church_Ruin_Stone_Arch_02_xjurabvs"), "Arch_Art", (5500, 0, 400), (160, 820, 820), yaw=90, folder="Art/Cliff")
    # hidden glass platforms: visual stone slabs that reveal with them
    slab = first_sm(f"{MS}/Medieval_ChurchRuin_Floor_Slab_Stone_xjvkfbega")
    n_sl = 0
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("Glass_") and unreal.Name("CliffPlatform") in a.tags:
            o, e = a.get_actor_bounds(False)
            s = fit(slab, f"Slab_{lab}", (o.x, o.y, o.z + e.z - 12), (e.x * 2.05, e.y * 2.05, 30), folder="Art/Cliff/Platforms")
            s.tags = ["CliffPlatform"]; s.set_actor_hidden_in_game(True)
            a.set_is_temporarily_hidden_in_editor(True)
            mats = a.static_mesh_component.get_num_materials()
            for i in range(mats): a.static_mesh_component.set_material(i, sm("/Game/TUM/Materials/Surfaces/M_Invisible"))
            n_sl += 1
    # far sea stacks poking out of the clouds
    for i, (x, y, h) in enumerate(((2500, 7000, 5000), (6000, -8000, 6000), (9500, 5000, 4500), (-3000, -6000, 5200), (12000, -1500, 7000))):
        fit(random.choice(massive), f"Peak_{i}", (x, y, h / 2 - 3200), (h * 0.8, h * 0.8, h), yaw=random.uniform(0, 360), uniform=True, folder="Art/Cliff/Peaks")
    L.save_current_level(); return {"slabs": n_sl}

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("dragon", dragon)
    step("cliff", cliff)
    return res
