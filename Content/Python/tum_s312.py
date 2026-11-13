# Factory as a place, not a corridor: worker stations by the looms, storage bays, a foreman's desk story beat, lamp spine, amber goal lights
import unreal, random, math, traceback
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; DC = "/Game/DerelictCorridor/Assets/Fab/Megascans/3D"; MS = "/Game/MS/3D"; F = "Art/Factory/Story"
def first(folder):
    ps = [p for p in EAL.list_assets(folder, False, False) if p.split("/")[-1].startswith("SM_")]
    return EAL.load_asset(ps[0])
def place(mesh, name, x, y, yaw=0.0, h=None, z=0.0, collide=True):
    a = E.spawn_actor_from_object(mesh, V(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    if h:
        o, e = a.get_actor_bounds(False); s = h / max(2 * e.z, 1); a.set_actor_scale3d(V(s, s, s))
    o, e = a.get_actor_bounds(False); l = a.get_actor_location()
    a.set_actor_location(V(l.x + x - o.x, l.y + y - o.y, l.z + z + e.z - o.z), False, False)
    if not collide: a.set_actor_enable_collision(False)
    a.set_actor_label(name); a.set_folder_path(F); return a
def light(name, x, y, z, color, inten, radius, spot=False, cone=40.0):
    cls = unreal.SpotLight if spot else unreal.PointLight
    a = E.spawn_actor_from_class(cls, V(x, y, z), unreal.Rotator(roll=0, pitch=-90 if spot else 0, yaw=0))
    c = a.spot_light_component if spot else a.point_light_component
    c.set_intensity(inten); c.set_light_color(unreal.LinearColor(*color, 1)); c.set_attenuation_radius(radius); c.set_cast_shadows(spot)
    if spot: c.set_outer_cone_angle(cone); c.set_inner_cone_angle(cone * 0.6)
    a.set_actor_label(name); a.set_folder_path(F); return a
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_FactoryHub")
    out = {}
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label()
        if lab.startswith("Prop_") or str(a.get_folder_path()).startswith(F): E.destroy_actor(a)
    random.seed(4)
    stool = first(f"{DC}/Res_Furn_Stool_Metal_Worn_01"); chair = first(f"{DC}/Res_Furn_Chair_Metal_Armless_01")
    rope = first(f"{MS}/Rope_Coil_vcsoddfs"); tangled = first(f"{MS}/Tangled_Rope_vhnofbds"); chains = first(f"{MS}/Pile_Of_Chains_uc1ufamhx")
    shelf = first(f"{DC}/Ind_Ware_Storage_Shelf_Metal_Rusted_01"); cab = first(f"{DC}/Ind_Ware_Storage_Cabinet_Metal_Rusty_01"); barrel = first(f"{MS}/Wooden_Barrel_tmgmfeefa")
    table = first(f"{DC}/Ind_Ware_Furn_Table_Wood_Worn_01"); suitcase = EAL.load_asset(f"{MS}/Leather_Luggage_Suitcase_wk2iafu/SM_S_StrapV1_N1")
    knight = EAL.load_asset("/Game/TUM/Props/PolyHaven/chess_set/chess_set/StaticMeshes/piece_knight_white_01")
    lamps = [first(f"{DC}/Ind_Ware_Light_Ceiling_Metal_Hanging_0{i}") for i in (1, 2, 3, 4)]
    hang = [EAL.load_asset(p) for p in EAL.list_assets(f"{MS}/Rusty_Hanging_Chain_wcwsfgudw", False, False) if p.split("/")[-1].startswith("SM_")]
    # 1) a worker's station beside every loom: stool, thread (rope) and the odd tangle on the floor
    n = 0
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith("LoomMachine_"):
            o, e = a.get_actor_bounds(False); side = -1 if o.y > 0 else 1
            sx, sy = o.x + random.uniform(-60, 60), o.y + side * (e.y + 55)
            place(stool if random.random() < 0.7 else chair, f"Station_Seat_{n}", sx, sy, yaw=random.uniform(0, 360), h=random.uniform(55, 65) if True else None)
            if random.random() < 0.6: place(rope, f"Station_Rope_{n}", o.x + random.uniform(-e.x, e.x), o.y + side * (e.y + 20), yaw=random.uniform(0, 360), h=18, collide=False)
            if random.random() < 0.35: place(tangled, f"Station_Tangle_{n}", sx + random.uniform(60, 120), sy, yaw=random.uniform(0, 360), h=12, collide=False)
            n += 1
    out["stations"] = n
    # 2) three storage bays against the walls (groups, not rows)
    for b, (bx, by, yaw) in enumerate(((750, -690, 90), (4650, 690, -90), (6050, -690, 90))):
        place(shelf, f"Bay{b}_Shelf", bx, by, yaw=yaw + random.uniform(-4, 4), h=220)
        place(cab, f"Bay{b}_Cab", bx + 170, by, yaw=yaw + random.uniform(-8, 8), h=190)
        for k in range(random.randint(2, 3)):
            place(barrel, f"Bay{b}_Barrel{k}", bx - 160 - k * 75 + random.uniform(-15, 15), by + random.uniform(-40, 40) * (1 if by < 0 else -1), yaw=random.uniform(0, 360), h=95)
        place(chains, f"Bay{b}_Chains", bx + 60, by + (90 if by < 0 else -90), yaw=random.uniform(0, 360), h=30, collide=False)
    # 3) the foreman's desk: her suitcase and a white knight -- the unfinished move, waiting
    place(table, "Story_Desk", 4300, -420, yaw=15, h=80)
    place(chair, "Story_Chair", 4300, -330, yaw=200, h=88)
    place(suitcase, "Story_Suitcase", 4180, -520, yaw=60, h=30, collide=False)
    k = place(knight, "Story_Knight", 4320, -425, yaw=140, h=12, z=80, collide=False)
    light("Story_Light", 4300, -420, 330, (1.0, 0.7, 0.4), 9000.0, 700.0, spot=True, cone=26.0)
    # 4) a spine of hanging lamps with warm pools so the hall reads in beats, plus hanging chains
    for i, x in enumerate(range(600, 7300, 950)):
        y = random.uniform(-120, 120)
        place(random.choice(lamps), f"Spine_Lamp_{i}", x, y, yaw=random.uniform(0, 90), h=70, z=520, collide=False)
        light(f"Spine_Light_{i}", x, y, 500, (1.0, 0.78, 0.5), 2600.0, 900.0)
    for i in range(7):
        if hang: place(random.choice(hang), f"Hang_Chain_{i}", random.uniform(800, 7000), random.uniform(-500, 500), yaw=random.uniform(0, 360), h=random.uniform(250, 420), z=random.uniform(380, 520), collide=False)
    # 5) every goal glows amber like Mara
    for i, (x, y, z) in enumerate(((3500, 0, 0), (5450, -575, 326), (6425, -575, 750), (8410, 0, 0))):
        light(f"Goal_Glow_{i}", x, y, z + 420, (1.0, 0.62, 0.28), 14000.0, 900.0, spot=True, cone=20.0)
    L.save_current_level(); return out
