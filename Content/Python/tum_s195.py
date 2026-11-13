# War field: real battlefield — Greystone soldiers (threats + crowd fighting/running), real ground, ruin boundaries, dusk light
import unreal, random, math, importlib, traceback
import tum_graph as TG; importlib.reload(TG)
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; MOV = unreal.ComponentMobility.MOVABLE; KW = unreal.AttachmentRule.KEEP_WORLD
MV = "/Game/TUM/Props/BP_Mover"; MS = "/Game/MS/3D"; SUR = "/Game/MS/Surfaces"; MAT = "/Game/TUM/Materials/Surfaces"
GS = "/Game/ParagonGreystone/Characters/Heroes/Greystone"
SKINS = [f"{GS}/Meshes/Greystone", f"{GS}/Skins/Tough/Meshes/Greystone_Tough", f"{GS}/Skins/Dragonlord/Meshes/Greystone_Dragonlord", f"{GS}/Skins/WhiteTiger/Meshes/Greystone_WhiteTiger"]
A = lambda n: EAL.load_asset(f"{GS}/Animations/{n}")
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a
def label(a, name, folder):
    a.set_actor_label(name); a.set_folder_path(folder); return a

# ---------- BP_Mover: optional facing of motion direction ----------
def mover_bp():
    TG.ensure_vars(MV, [("BaseYaw", "float"), ("bFaceMotion", "bool")])
    g = lambda n: f"(Variables|Default|Get{n})"
    code = f"""
(event EventBeginPlay
  (bind l (Transformation|GetActorLocation))
  (Variables|Default|SetBaseX (.x l))
  (Variables|Default|SetBaseY (.y l))
  (Variables|Default|SetBaseZ (.z l))
  (Variables|Default|SetBaseYaw (.z (Transformation|GetActorRotation)))
  (Actor|Tick|SetActorTickEnabled :bEnabled (not {g('StartDisabled')})))

(event EventTick (DeltaSeconds)
  (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
  (bind s (Math|Trig|Sin(Radians) (+ (* {g('T')} {g('Speed')}) {g('Phase')})))
  (Transformation|SetActorLocation :NewLocation (Math|Vector|MakeVector (+ {g('BaseX')} (* {g('AmpX')} s)) (+ {g('BaseY')} (* {g('AmpY')} s)) (+ {g('BaseZ')} (* {g('AmpZ')} s))) :bTeleport true)
  (if {g('FaceMotion')}
    (if (< (Math|Trig|Cos(Radians) (+ (* {g('T')} {g('Speed')}) {g('Phase')})) 0.0)
      (Transformation|SetActorRotation :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (+ {g('BaseYaw')} 180.0)) :bTeleportPhysics true)
      (else (Transformation|SetActorRotation :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw {g('BaseYaw')}) :bTeleportPhysics true))))
  (if (and (> {g('KillRadius')} 0.0) (< (Transformation|GetDistanceTo :OtherActor (Game|GetPlayerCharacter 0)) {g('KillRadius')}))
    (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object (Game|GetPlayerCharacter 0))
      (:then (Class|BPTUMCharacter|Respawn :self ch))
      (:CastFailed))))
"""
    r = TG.run(MV, code, clear=True)
    b = EAL.load_asset(MV); BEL = unreal.BlueprintEditorLibrary
    for n in ("AmpX", "AmpY", "AmpZ", "Speed", "Phase", "KillRadius", "bStartDisabled", "bFaceMotion"): BEL.set_blueprint_variable_instance_editable(b, n, True)
    BEL.compile_blueprint(b); EAL.save_loaded_asset(b, False); return str(r)[:300]

# ---------- materials ----------
def tri(name, base, tile, tint=(1, 1, 1), rough=1.0):
    p = f"{MAT}/{name}"
    mi = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(name, MAT, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, EAL.load_asset(f"{MAT}/MAT_TriplanarORM"))
    for k, suf in (("BaseColor", "_D"), ("Normal", "_N")):
        t = EAL.load_asset(base[0] + suf); t.set_editor_property("virtual_texture_streaming", False); EAL.save_loaded_asset(t, False)
        MEL.set_material_instance_texture_parameter_value(mi, k, t)
    o = EAL.load_asset(base[1]); o.set_editor_property("virtual_texture_streaming", False); o.set_editor_property("srgb", False); EAL.save_loaded_asset(o, False)
    MEL.set_material_instance_texture_parameter_value(mi, "ORM", o)
    MEL.set_material_instance_scalar_parameter_value(mi, "TileSize", tile)
    MEL.set_material_instance_scalar_parameter_value(mi, "MetallicMul", 0.0)
    MEL.set_material_instance_scalar_parameter_value(mi, "RoughnessMul", rough)
    MEL.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(*tint, 1))
    EAL.save_loaded_asset(mi, False); return mi
def mats():
    soil = tri("MI_War_Soil", (f"{SUR}/Soil_Ground_xdhhdhl/T_Soil_Ground_xdhhdhl", f"{SUR}/Soil_Ground_xdhhdhl/T_SoilGround_xdhhdhl_ORDp"), 350.0)
    mud = tri("MI_War_Mud", (f"{SUR}/Dry_Sandy_Mud_wdunfjf/T_Dry_Sandy_Mud_wdunfjf", f"{SUR}/Dry_Sandy_Mud_wdunfjf/T_DrySandyMud_wdunfjf_ORDp"), 300.0, (0.45, 0.38, 0.32), 0.45)
    grass = tri("MI_War_Burnt", (f"{SUR}/Burnt_Grass_smlmnnn/T_Burnt_Grass_smlmnnn", f"{SUR}/Burnt_Grass_smlmnnn/T_BurntGrass_smlmnnn_DpRA"), 400.0, (0.8, 0.75, 0.65))
    rocky = tri("MI_War_Rocky", (f"{SUR}/Rocky_Soil_Ground_vb2qdgwew/T_Rocky_Soil_Ground_vb2qdgwew", f"{SUR}/Rocky_Soil_Ground_vb2qdgwew/T_RockySoilGround_vb2qdgwew_ORDp"), 400.0)
    return soil, mud, grass, rocky

# ---------- static props ----------
def sm(path):
    m = EAL.load_asset(path)
    if not m: raise RuntimeError("missing " + path)
    return m
def put(mesh, name, x, y, z, yaw, h=None, length=None, scale=None, folder="Art/War/Dress", collide=False, pitch=0.0, roll=0.0):
    m = sm(mesh) if isinstance(mesh, str) else mesh
    a = E.spawn_actor_from_object(m, V(x, y, z), unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw))
    b = m.get_bounding_box(); ext = b.max - b.min
    s = scale or 1.0
    if h: s = h / max(ext.z, 1)
    if length: s = length / max(ext.x, ext.y, 1)
    a.set_actor_scale3d(V(s, s, s))
    if not collide: a.set_actor_enable_collision(False); a.static_mesh_component.set_collision_profile_name("NoCollision")
    return label(a, name, folder)

def ground(soil, mud, grass, rocky):
    out = []
    for n, mi in (("Start_Floor", grass), ("End_Floor", soil), ("Floor_Cover", grass), ("Floor_Trench", soil)) + tuple((f"Mud_{i}", mud) for i in range(4)):
        a = find(n)
        if a: a.static_mesh_component.set_material(0, mi); out.append(n)
    # wide battlefield ground beyond the walls (fades into fog)
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith(("War_Ground", "War_Pit")): E.destroy_actor(a)
    g = E.spawn_actor_from_object(sm("/Engine/BasicShapes/Plane"), V(3000, 0, -8), unreal.Rotator())
    g.set_actor_scale3d(V(900, 900, 1)); g.static_mesh_component.set_material(0, soil); label(g, "War_Ground", "Art/War/Ground")
    g.set_actor_enable_collision(False)
    # mud pits under the gaps of the right lane
    for i, (x0, x1) in enumerate(((1500, 2100), (3000, 3600), (4400, 5000))):
        p = E.spawn_actor_from_object(sm("/Engine/BasicShapes/Plane"), V((x0 + x1) / 2, 1565, -120), unreal.Rotator())
        p.set_actor_scale3d(V((x1 - x0) / 100 + 0.4, 15.0, 1)); p.static_mesh_component.set_material(0, mud); label(p, f"War_Pit_{i}", "Art/War/Ground"); p.set_actor_enable_collision(False)
    return out

def bounds_and_dress():
    random.seed(1408)
    for a in list(E.get_all_level_actors()):
        if str(a.get_folder_path()).startswith("Art/War/Dress"): E.destroy_actor(a)
    # graybox walls stay as invisible collision only
    for n in ("Wall_Back", "Wall_S", "Wall_N", "Wall_End"):
        a = find(n)
        if a: a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True)
    ruins = [f"{MS}/Modular_Ruins_Wall_vdcjbgo/SM_Ruins_Wall_vdcjbgo_N1", f"{MS}/Modular_Broken_Brick_Walls_Kit_xjotaibiy/SM_Modular_Broken_Brick_Walls_Kit_xjotaibiy_00_N1",
             f"{MS}/Modular_Broken_Brick_Walls_Kit_xjotaibiy/SM_Modular_Broken_Brick_Walls_Kit_xjotaibiy_01_N1", f"{MS}/Modular_Broken_Brick_Walls_Kit_xjotaibiy/SM_Modular_Broken_Brick_Walls_Kit_xjotaibiy_02_N1",
             f"{MS}/Modular_ChurchRuin_Stone_Kit_yh3kddhiy/SM_Modular_ChurchRuin_Stone_Kit_yh3kddhiy_00_N1"]
    stakes = f"{MS}/Stakes_And_Wedges_Pack_tl2effiva/SM_Stakes_And_WedgeSM_Pack_tl2effiva_00_N1"
    trees = [f"{MS}/Dead_Tree_rlthg/SM_Dead_Tree_rlthg_01_N1"] + [p for p in EAL.list_assets(f"{MS}/Dead_Tree_qlEtl", False, False) if "/SM_" in p][:2]
    n = 0
    # broken, irregular boundary along both long sides (never a clean row)
    for side in (-1, 1):
        x = -200
        while x < 6700:
            seg = random.uniform(500, 900); y = side * (2330 + random.uniform(-60, 140))
            kind = random.random()
            if kind < 0.6:
                put(random.choice(ruins), f"Ruin_{n}", x + seg / 2, y, -10, (0 if side < 0 else 180) + random.uniform(-14, 14), length=seg * random.uniform(0.75, 1.05))
            elif kind < 0.85:
                put(stakes, f"Stakes_{n}", x + seg / 2, y, 0, 90 + random.uniform(-25, 25), length=seg * 0.8)
            else:
                put(random.choice(trees), f"DeadTree_{n}", x + seg / 2, y + side * random.uniform(0, 200), -20, random.uniform(0, 360), h=random.uniform(700, 1100))
            n += 1; x += seg + random.uniform(-80, 220)
    for y in (-1700, -500, 600, 1800):  # back and end
        put(random.choice(ruins), f"Ruin_{n}", -360 + random.uniform(-40, 40), y + random.uniform(-150, 150), -10, 90 + random.uniform(-12, 12), length=random.uniform(900, 1300)); n += 1
        put(random.choice(ruins), f"Ruin_{n}", 6680 + random.uniform(-40, 60), y + random.uniform(-150, 150), -10, -90 + random.uniform(-12, 12), length=random.uniform(900, 1300)); n += 1
    # far horizon: cliffs, ruined towers, burning trees
    cliffs = [f"{MS}/Massive_Nordic_Coastal_Cliff_ullqbb1ga/SM_Massive_Nordic_Coastal_Cliff_ullqbb1ga_N1"] + [p for p in EAL.list_assets(f"{MS}/Huge_Nordic_Coastal_Cliff_ulkiejkva", False, False) if "/SM_" in p][:1]
    for i, (x, y, yaw, h) in enumerate(((1500, 16000, 170, 5200), (9500, 15000, 200, 6400), (-6000, 11000, 120, 4800), (4000, -17000, 10, 5600), (12000, -9000, -60, 4500), (-7000, -12000, 40, 5000))):
        put(random.choice(cliffs), f"Horizon_Cliff_{i}", x, y, -600, yaw, h=h)
    arch = f"{MS}/Modular_Church_Ruin_Stone_Arch_02_xjurabvs/SM_Modular_Church_Ruin_Stone_Arch_02_xjurabvs_00_N1"
    col = f"{MS}/Medieval_Church_Ruin_Column_01_xjsofces/SM_Medieval_Church_Ruin_External_Column_01_xjsofces_N1"
    for i, (x, y, yaw) in enumerate(((2200, 7200, 8), (4700, 8200, -15), (7600, 6400, 30), (900, -7600, 190), (5200, -8100, 170))):
        put(arch, f"Far_Arch_{i}", x, y, -30, yaw, h=random.uniform(1300, 1700)); put(col, f"Far_Col_{i}", x + random.uniform(500, 900), y + random.uniform(-300, 300), -30, random.uniform(0, 360), h=random.uniform(900, 1400))
    for i in range(14):
        x = random.uniform(-2500, 9000); y = random.choice((-1, 1)) * random.uniform(3200, 9000)
        put(random.choice(trees), f"Field_Tree_{i}", x, y, -30, random.uniform(0, 360), h=random.uniform(600, 1200))
    # fires: warm glow pools on the battlefield
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Fire_Glow"): E.destroy_actor(a)
    for i, (x, y) in enumerate(((800, 3600), (3300, 4400), (5600, 3300), (2100, -3900), (4800, -4600), (-300, -3200), (6900, -2800))):
        l = E.spawn_actor_from_class(unreal.PointLight, V(x, y, 180), unreal.Rotator()); c = l.point_light_component
        c.set_intensity(60000.0); c.set_light_color(unreal.LinearColor(1.0, 0.42, 0.12, 1)); c.set_attenuation_radius(2200.0); c.set_cast_shadows(False)
        label(l, f"Fire_Glow_{i}", "Art/War/Dress")
        put(f"{MS}/Worn_Wooden_Beam_tgmsdc0fa/SM_Worn_Wooden_Beam_tgmsdc0fa_00_N1", f"Fire_Logs_{i}a", x, y, 10, random.uniform(0, 180), length=380, pitch=8)
        put(f"{MS}/Worn_Wooden_Beam_tgmsdc0fa/SM_Worn_Wooden_Beam_tgmsdc0fa_01_N1", f"Fire_Logs_{i}b", x + 40, y - 30, 20, random.uniform(0, 180), length=320, pitch=-12)
    return n

def graybox_cleanup():
    out = []
    for n in ("Rope", "Seal_Hanging", "Seal_Ground", "Shrine_Pillar_S", "Shrine_Pillar_N", "Shrine_Lintel", "Cover_Wall_0", "Cover_Wall_1", "Cover_Wall_2", "Wagon_0", "Wagon_1", "Wagon_2", "LaneWall_L", "LaneWall_R"):
        a = find(n)
        if not a: continue
        if n in ("Rope", "Seal_Hanging", "Seal_Ground"):
            a.tags = []; a.set_actor_hidden_in_game(True); a.set_actor_enable_collision(False)
        else:
            a.set_actor_hidden_in_game(True)
        a.set_is_temporarily_hidden_in_editor(True); out.append(n)
    return out

# ---------- soldiers ----------
def soldier(name, x, y, z, yaw, anim, skin=None, rate=1.0, pos=0.0, folder="Art/War/Soldiers", shadow=True):
    a = E.spawn_actor_from_class(unreal.SkeletalMeshActor, V(x, y, z), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    c = a.skeletal_mesh_component; c.set_mobility(MOV)
    mesh = EAL.load_asset(skin or random.choice(SKINS))
    try: c.set_skeletal_mesh_asset(mesh)
    except Exception: c.set_editor_property("skeletal_mesh_asset", mesh)
    c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    d = unreal.SingleAnimationPlayData()
    d.set_editor_property("anim_to_play", A(anim)); d.set_editor_property("saved_looping", True); d.set_editor_property("saved_playing", True)
    d.set_editor_property("saved_position", pos); d.set_editor_property("saved_play_rate", rate)
    c.set_editor_property("animation_data", d); c.set_cast_shadow(shadow)
    c.set_collision_profile_name("NoCollision"); a.set_actor_enable_collision(False)
    return label(a, name, folder)
def mover(name, x, y, z, yaw, amp, speed, phase, kill=0.0, folder="Art/War/Soldiers"):
    mv = E.spawn_actor_from_class(EAL.load_asset(MV).generated_class(), V(x, y, z), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    mv.root_component.set_mobility(MOV)
    for k, v in (("AmpX", float(amp[0])), ("AmpY", float(amp[1])), ("AmpZ", 0.0), ("Speed", float(speed)), ("Phase", float(phase)), ("KillRadius", float(kill)), ("bFaceMotion", True)):
        mv.set_editor_property(k, v)
    return label(mv, name, folder)
FIGHT = ["Attack_A_Fast", "Attack_B_Fast", "Attack_C_Med", "Attack_D_Fast", "Attack_A_Med", "Attack_B_Med", "Attack_PrimaryA", "Attack_PrimaryB", "Attack_PrimaryC"]
DEF = ["Deflect_InPlace", "HitReact_Front", "Attack_C_Fast", "Attack_D_Med"]

def soldiers():
    random.seed(77)
    for a in list(E.get_all_level_actors()):
        if str(a.get_folder_path()).startswith("Art/War/Soldiers"): E.destroy_actor(a)
    n = 0
    # threats: the three crossing soldiers + the rider on the cover lane keep their movers; the box bodies become knights
    for tname, skin in (("Soldier_0", SKINS[1]), ("Soldier_1", SKINS[2]), ("Soldier_2", SKINS[3]), ("Rider_Cover", SKINS[0])):
        mv = find(tname); body = find(tname + "_Body")
        if not mv: continue
        mv.set_editor_property("bFaceMotion", True); mv.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=90), False)
        if body: body.set_actor_hidden_in_game(True); body.set_is_temporarily_hidden_in_editor(True); body.set_actor_enable_collision(False)
        l = mv.get_actor_location()
        k = soldier(f"Knight_{tname}", l.x, l.y, 12, 0, "TravelMode_Fwd" if tname != "Rider_Cover" else "Jog_Fwd", skin=skin, folder="War/Threats")
        k.attach_to_actor(mv, "", KW, KW, KW, False); n += 1
    # crowd beyond both long walls: runners crossing the battlefield and duels
    for side in (-1, 1):
        for i in range(13):
            x = random.uniform(-1500, 8000); y = side * random.uniform(2900, 6500)
            if random.random() < 0.55:   # runner along X
                amp = random.uniform(900, 2200); sp = random.uniform(380, 560) / amp; fwd = random.choice((0, 180))
                mv = mover(f"Crowd_Run_{n}", x, y, 0, fwd, (amp if fwd == 0 else -amp, 0), sp, random.uniform(0, 6.28))
                s = soldier(f"Crowd_RunMesh_{n}", x, y, 4, fwd - 90, "TravelMode_Fwd", rate=random.uniform(0.9, 1.1), pos=random.uniform(0, 1), shadow=abs(y) < 4500)
                s.attach_to_actor(mv, "", KW, KW, KW, False)
            else:                         # charging toward / away from the field along Y
                amp = random.uniform(700, 1400); sp = random.uniform(380, 520) / amp; fwd = 90 if side < 0 else -90
                mv = mover(f"Crowd_Run_{n}", x, y, 0, fwd, (0, amp if fwd == 90 else -amp), sp, random.uniform(0, 6.28))
                s = soldier(f"Crowd_RunMesh_{n}", x, y, 4, fwd - 90, "Jog_Fwd", rate=random.uniform(0.95, 1.15), pos=random.uniform(0, 1), shadow=abs(y) < 4500)
                s.attach_to_actor(mv, "", KW, KW, KW, False)
            n += 1
        for i in range(8):   # duels
            x = random.uniform(-1200, 7800); y = side * random.uniform(2800, 5600); yaw = random.uniform(0, 360)
            dx, dy = math.cos(math.radians(yaw)) * 85, math.sin(math.radians(yaw)) * 85
            soldier(f"Duel_{n}a", x - dx, y - dy, 4, yaw - 90, random.choice(FIGHT), skin=random.choice(SKINS[:2]), rate=random.uniform(0.85, 1.1), pos=random.uniform(0, 1))
            soldier(f"Duel_{n}b", x + dx, y + dy, 4, yaw + 90, random.choice(DEF + FIGHT), skin=random.choice(SKINS[2:]), rate=random.uniform(0.85, 1.1), pos=random.uniform(0, 1))
            n += 1
    # inside the field, away from the routes: duels in the corners of the start and end grounds (harmless)
    for i, (x, y) in enumerate(((150, -1900), (300, 1850), (5600, -1700), (6250, 1600), (5450, 1950))):
        yaw = random.uniform(0, 360); dx, dy = math.cos(math.radians(yaw)) * 85, math.sin(math.radians(yaw)) * 85
        soldier(f"Duel_In_{i}a", x - dx, y - dy, 4, yaw - 90, random.choice(FIGHT), skin=SKINS[0], pos=random.uniform(0, 1))
        soldier(f"Duel_In_{i}b", x + dx, y + dy, 4, yaw + 90, random.choice(DEF), skin=SKINS[2], pos=random.uniform(0, 1))
    return n

def light():
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab == "Sun":
            a.set_actor_rotation(unreal.Rotator(roll=0, pitch=-9, yaw=150), False)
            c = a.light_component; c.set_intensity(4.0); c.set_light_color(unreal.LinearColor(1.0, 0.55, 0.32, 1))
        if isinstance(a, unreal.ExponentialHeightFog):
            f = a.component; f.set_fog_density(0.035); f.set_fog_inscattering_color(unreal.LinearColor(0.42, 0.25, 0.16, 1))
            f.set_editor_property("fog_height_falloff", 0.12)
        if isinstance(a, unreal.SkyLight): a.light_component.set_intensity(0.7); a.light_component.recapture_sky()
    return "ok"

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("mover_bp", mover_bp)
    L.load_level("/Game/TUM/Maps/M_Cut_WarField")
    m = [None]
    step("mats", lambda: m.__setitem__(0, mats()))
    if m[0]: step("ground", lambda: ground(*m[0]))
    step("cleanup", graybox_cleanup)
    step("dress", bounds_and_dress)
    step("soldiers", soldiers)
    step("light", light)
    L.save_current_level()
    return res
