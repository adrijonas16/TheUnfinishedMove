import unreal, importlib, traceback
import tum_art as A; importlib.reload(A)
def war():
    A.LES().load_level("/Game/TUM/Maps/M_Cut_WarField"); A.clear(); W = "Art/War"
    # background: cliffs and ruined castle silhouettes on the horizon
    for i, (x, y, yaw) in enumerate(((2500, -4200, 0), (5200, -4400, 40), (8200, -1500, 90), (8000, 1800, 120), (3000, 4300, 180), (-1500, 3800, 220))):
        A.place("Massive_Nordic_Coastal_Cliff", x, y, -200, size=(3000, None, None), yaw=yaw, folder=W + "/Horizon")
    for i, (x, y) in enumerate(((7400, -900), (7600, 700), (7300, 2000))):
        A.place("Modular_ChurchRuin_Stone_Kit", x, y, 0, size=(None, None, 1400), yaw=90 + i * 25, folder=W + "/Horizon")
    # lane walls dressed with broken brick ruin walls
    for side, y in (("L", -800), ("R", 800)):
        for i, x in enumerate(range(700, 5200, 500)):
            A.place("Modular_Broken_Brick_Walls_Kit", x + 250, y, 0, size=(520, None, 320), uniform=False, yaw=0, folder=W + "/LaneWalls")
    A.hide_box("LaneWall")
    # cover route: ruin wall chunks on the cover walls
    for i, x in enumerate((1400, 2600, 3800)):
        y0, y1 = (-2300, -1450) if i % 2 == 0 else (-1650, -830)
        A.place("Ruins_Wall", x + 60, (y0 + y1) / 2, 0, size=(None, abs(y1 - y0), 320), uniform=False, yaw=90, folder=W + "/Cover")
    A.hide_box("Cover_Wall")
    # wagons -> crates, barrels, boards
    for i, (x, y) in enumerate(((1600, -300), (2800, 300), (4000, -200))):
        A.place("Old_Wooden_Crate_vkgrchzga_01", x + 80, y - 40, 0, size=(None, None, 150), yaw=10 * i, folder=W + "/Wagons")
        A.place("Old_Wooden_Crate_vkgrchzga_02", x + 230, y + 40, 0, size=(None, None, 120), yaw=-15, folder=W + "/Wagons")
        A.place("Wooden_Barrel", x + 160, y + 90, 0, size=(None, None, 110), folder=W + "/Wagons")
        A.place("Old_Wood_Boards_ricaS_0" + str(i), x + 150, y, 150, size=(320, None, None), yaw=90, folder=W + "/Wagons")
    A.hide_box("Wagon_")
    # stakes along the trench and dry grass everywhere
    for i, x in enumerate(range(900, 5100, 700)):
        A.place("Stakes_And_Wedge", x, -720 if i % 2 else 720, 0, size=(None, None, 160), yaw=i * 37, folder=W + "/Stakes")
    A.scatter(["Dry_Grass_tbbqejqr_01", "Dry_Grass_tbbqejqr_02", "Dry_Grass_tbbqejqr_03", "Dry_Grass_tbbqejqr_04", "Dry_Grass_tbbqejqr_05"], 140, 0, 6500, -2250, -850, seed=3, size=(None, None, 90))
    A.scatter(["Dry_Grass_tbbqejqr_02", "Dry_Grass_tbbqejqr_04"], 90, 600, 5200, -750, 750, seed=4, size=(None, None, 70))
    A.scatter(["Dead_Tree_qlEtl", "Dead_Tree_rlthg"], 7, -200, 6400, -2200, -1800, seed=5, size=(None, None, 700), smin=0.8, smax=1.2)
    A.scatter(["Skull", "Tree_Branch_pbbau", "Tree_Branch_pcsvQ", "Old_Wooden_Pole"], 25, 600, 5200, -2200, 2200, seed=6, smin=0.9, smax=1.3)
    # shrine: church ruin arch, rope, the sword that cuts it
    A.place("Modular_Church_Ruin_Stone_Arch_02", 5900, 0, 0, size=(None, 700, 900), uniform=False, yaw=90, folder=W + "/Shrine")
    A.hide_box("Shrine_")
    A.place("Sword_uitlbiaga", 5780, 140, 0, size=(None, None, 110), pitch=0, roll=8, folder=W + "/Shrine")
    A.place("Rope_Coil", 5960, -180, 0, size=(80, None, None), folder=W + "/Shrine")
    A.place("Medieval_Floor_Slab_Stone", 5900, 0, 0, size=(900, 900, None), uniform=False, folder=W + "/Shrine")
    A.LES().save_current_level(); return "ok"
def cliff():
    A.LES().load_level("/Game/TUM/Maps/M_Cut_Cliff"); A.clear(); C = "Art/Cliff"
    A.place("Huge_Nordic_Coastal_Cliff_ulkiejkva_01", -200, 0, -2300, size=(1400, 1600, 2300), uniform=False, yaw=0, folder=C)
    A.place("Huge_Nordic_Coastal_Cliff_venrdcgga_01", 5500, 0, -2300, size=(1400, 1700, 2300), uniform=False, yaw=180, folder=C)
    A.hide_box("Start_Ledge"); A.hide_box("End_Ledge"); A.hide_box("Start_CliffWall")
    for i, (x, y, h) in enumerate(((1500, -2600, 4200), (3200, -3100, 5200), (4800, -2500, 3800), (1800, 2800, 4600), (3600, 3300, 5600), (5600, 2600, 4000), (7600, 0, 6000))):
        A.place("Massive_Nordic_Coastal_Cliff", x, y, -2300, size=(None, None, h), yaw=i * 61, folder=C + "/Pillars")
    A.place("Modular_Church_Ruin_Stone_Arch_02", 5500, 0, 0, size=(None, 820, 900), uniform=False, yaw=90, folder=C)
    A.hide_box("Arch_Pillar"); A.hide_box("Arch_Lintel")
    A.scatter(["Nordic_Beach_Rock_uknnfet_01", "Nordic_Beach_Rock_uk3lcj2ga_01", "Nordic_Beach_Stone"], 10, -500, 350, -450, 450, z=0, seed=7, smin=0.4, smax=0.8)
    A.LES().save_current_level(); return "ok"
def factory():
    A.LES().load_level("/Game/TUM/Maps/M_FactoryHub"); A.clear(); F = "Art/Factory"
    for i, x in enumerate(range(200, 7400, 900)):
        A.place("SM_Ind_Ware_Light_Ceiling_Metal_Hanging_0" + str(1 + i % 4), x + 380, 0, 900, size=(None, None, 200), folder=F + "/Lights")
        A.place("Rusty_Hanging_Chain_wcwsf", x + 150, 380 if i % 2 else -380, 600, size=(None, None, 500), folder=F + "/Chains")
    for i, x in enumerate(range(0, 7400, 600)):
        A.place("SM_Ind_Set_Pipe_Metal_Mod_01_" + "ABCDEFG"[i % 7], x, 770, 700, size=(600, None, None), yaw=0, folder=F + "/Pipes")
        A.place("SM_Cables_01_Cables_Wall_Medium_0" + str(1 + i % 4), x + 300, -780, 450, size=(None, None, 300), yaw=90, folder=F + "/Cables")
    A.scatter(["SM_Ind_Rubble_Debris_Concrete_Pack_01_A", "SM_Ind_Rubble_Debris_Concrete_Pack_01_C", "SM_Ind_Rubble_Debris_Plank_Wood_Broken_01", "SM_Ind_Ware_Storage_Sheet_Cardboard_Flat_06_A"], 40, 0, 7400, -760, 760, seed=9, smin=0.8, smax=1.2)
    for i, (x, y) in enumerate(((300, -600), (900, 620), (4200, 650), (5000, -650), (7300, 620), (8000, -900), (9300, 900))):
        A.place("SM_Ind_Ware_Storage_Pallet_Wood_Worn_01", x, y, 0, yaw=i * 23, folder=F + "/Props")
        A.place("SM_Ind_Container_Oil_Plastic_Pack_01_" + "ABCDEF"[i % 6], x + 60, y, 15, yaw=i * 41, folder=F + "/Props")
    for i, x in enumerate((7700, 8300, 9000, 9600)):
        for y in (-1050, 1050): A.place("SM_Pillar_01", x, y, 0, size=(None, None, 1400), uniform=False, folder=F + "/Nave")
    A.place("SM_Ind_Ware_Furn_Table_Wood_Worn_01_A", 8800, 0, 0, size=(220, None, 80), uniform=False, folder=F + "/Chess")
    A.place("SM_Res_Furn_Chair_Metal_Armless_01", 8800, -200, 0, yaw=90, folder=F + "/Chess")
    A.place("SM_Res_Furn_Chair_Metal_Armless_01", 8800, 200, 0, yaw=-90, folder=F + "/Chess")
    A.LES().save_current_level(); return "ok"
def run(steps=("war", "cliff", "factory")):
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    res = {"err": {}}
    for s in steps:
        try: res[s] = globals()[s]()
        except Exception: res["err"][s] = traceback.format_exc()[-1200:]
    A.LES().load_level("/Game/TUM/Maps/M_FactoryHub"); return res
