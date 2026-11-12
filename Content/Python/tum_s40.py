# Maps batch: factory consequences + chess escape, War, Cliff, Real Room bookends
import unreal, importlib, traceback, math
import tum_lib as T; importlib.reload(T)
EAL = unreal.EditorAssetLibrary; V = T.V; G, D = T.GRID, T.GRID_DARK
MV, TR, AN, RR, DR = "/Game/TUM/Props/BP_Mover", "/Game/TUM/Core/BP_Trigger", "/Game/TUM/Verbs/BP_AlignAnchor", "/Game/TUM/Core/BP_RealRoomRoute", "/Game/TUM/Factory/BP_FactoryRoute"
KW = unreal.AttachmentRule.KEEP_WORLD; MOV = unreal.ComponentMobility.MOVABLE
def cls(p): return EAL.load_asset(p).generated_class()
def find(label):
    for a in T.EAS().get_all_level_actors():
        if a.get_actor_label() == label: return a
def hide(*acts):
    for a in acts: a.set_actor_hidden_in_game(True); a.set_actor_enable_collision(False)
def props(a, **kw):
    for k, v in kw.items(): a.set_editor_property(k, v)
def mover(label, x, y, z, size, amp=(0, 0, 0), speed=1.0, phase=0.0, kill=0.0, tags=(), disabled=False, m=D, folder="Movers", hidden=False):
    mv = T.EAS().spawn_actor_from_class(cls(MV), V(x, y, z), T.R()); mv.root_component.set_mobility(MOV)
    props(mv, AmpX=float(amp[0]), AmpY=float(amp[1]), AmpZ=float(amp[2]), Speed=float(speed), Phase=float(phase), KillRadius=float(kill), bStartDisabled=disabled)
    T.tag(mv, label, folder, tags)
    sx, sy, sz = size
    b = T.box(label + "_Body", x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2, m, folder, tags)
    b.root_component.set_mobility(MOV); b.attach_to_actor(mv, "", KW, KW, KW, False)
    if hidden: hide(mv, b)
    return mv
def trig(label, x, y, z, radius, show="None", hide_=("None", "None"), flag=0, target=None, disabled=False, tags=(), folder="Triggers"):
    t = T.EAS().spawn_actor_from_class(cls(TR), V(x, y, z), T.R())
    props(t, Radius=float(radius), ShowTag=show, HideTag=hide_[0], HideTag2=hide_[1], Flag=flag, bOpenMap=bool(target), TargetMap=target or "M_FactoryHub", bStartDisabled=disabled)
    return T.tag(t, label, folder, tags)
def anchor(label, x, y, z, target_actor, target_map="None", reveal=None, reveal_time=10.0, radius=320.0, mindot=0.996, save_return=True, tags=()):
    a = T.EAS().spawn_actor_from_class(cls(AN), V(x, y, z), T.R())
    props(a, TargetMap=target_map, AlignTarget=target_actor, Radius=radius, MinDot=mindot, bRevealOnly=bool(reveal), RevealTag=reveal or "None", RevealTime=reveal_time, bSaveReturn=save_return)
    return T.tag(a, label, "Gameplay", tags)
def player_start(x, y, z, yaw=0.0):
    for a in T.EAS().get_all_level_actors():
        if isinstance(a, unreal.PlayerStart): T.EAS().destroy_actor(a)
    ps = T.EAS().spawn_actor_from_class(unreal.PlayerStart, V(x, y, z), T.R(y=yaw)); ps.set_actor_label("PlayerStart"); ps.set_folder_path("Markers")
def cp(label, x, y, z=100): return T.point(label, x, y, z, "Markers/Checkpoints", ("Checkpoint",))
def ramp(label, x0, x1, y0, y1, z0, z1, m, folder, tags=()):
    L = math.hypot(x1 - x0, z1 - z0); pitch = math.degrees(math.atan2(z1 - z0, x1 - x0))
    a = T.box(label, -L / 2, L / 2, y0, y1, -12, 12, m, folder, tags)
    a.set_actor_location(V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2 - 12), False, False); a.set_actor_rotation(T.R(p=pitch), False); return a

def factory():
    T.LES().load_level("/Game/TUM/Maps/M_FactoryHub")
    for a in T.EAS().get_all_level_actors():
        if unreal.Name("S40") in a.tags: T.EAS().destroy_actor(a)
    S = ("S40",)
    cw = find("Catwalk_Raised"); o, e = cw.get_actor_bounds(False); cy, top = o.y, o.z + e.z
    # Factory I: patrol light on the loom lane centre line (hide in the loom rows / behind fabric)
    pm = mover("PatrolLight", 2750, 0, 110, (70, 70, 200), amp=(1000, 0, 0), speed=0.45, kill=260.0, tags=S + ("FocusPause",), m=D)
    l = T.light("PatrolLight_Lamp", 2750, 0, 260, (0.85, 0.92, 1.0), 9000.0, 700.0, "Movers", cls=unreal.SpotLight, rot=T.R(p=-90))
    l.tags = l.tags + [unreal.Name("S40"), unreal.Name("FocusPause")]; l.root_component.set_mobility(MOV); l.attach_to_actor(pm, "", KW, KW, KW, False)
    # Factory II -> War: Match Cut from the raised catwalk (torn banner lines up with the red window on the nave wall)
    far = T.box("Anchor_War_Window", 9760, 9790, cy - 160, cy + 160, top + 450, top + 750, D, "Graybox/Anchor", S)
    T.box("Anchor_War_Banner", 6900, 6920, cy - 70, cy + 70, top + 300, top + 480, D, "Graybox/Anchor", S, collide=False)
    anchor("AlignAnchor_War", 5450, cy, top + 100, far, "M_Cut_WarField", tags=S + ("CutAnchor_War",))
    T.box("Anchor_War_Spot", 5350, 5550, cy - 90, cy + 90, top, top + 3, D, "Graybox/Anchor", S, mesh=T.CYL, collide=False)
    # Factory III: after War the fabric bridge (ramp) climbs from the catwalk to the high ledge with the Cliff anchor
    hide(ramp("WarBridge_Ramp", 5700, 6250, cy - 110, cy + 110, top, 750, G, "Graybox/WarBridge", S + ("WarBridge",)))
    T.box("Cliff_Ledge", 6250, 6600, cy - 220, cy + 220, 725, 750, D, "Graybox/WarBridge", S)
    cfar = T.box("Anchor_Cliff_Slit", 9760, 9790, cy - 40, cy + 40, 1000, 1350, G, "Graybox/Anchor", S)
    anchor("AlignAnchor_Cliff", 6450, cy, 850, cfar, "M_Cut_Cliff", tags=S + ("CutAnchor_Cliff",))
    # Factory IV: Focus Gate — walls with one passage, a crusher that only a Focus Cut makes easy
    for nm, y0, y1 in (("S", -800, -150), ("N", 150, 800)):
        T.box(f"FocusGate_Wall{nm}", 7000, 7100, y0, y1, 0, 1100, D, "Graybox/FocusGate", S)
    mover("FocusGate_Crusher", 7050, 0, 330, (100, 300, 400), amp=(0, 0, 210), speed=2.4, kill=190.0, tags=S + ("FocusPause",), m=G, folder="Graybox/FocusGate")
    # Chess escape: three piece pads, one exit cell with three different ways in
    for i, (nm, y) in enumerate((("Block", -350), ("Diag", 0), ("Expose", 350))):
        T.box(f"ChessPad_{nm}", 8380, 8440, y - 30, y + 30, 0, 120 + 30 * i, G, "Chess/Pads", S + ("ChessPad",))
    trig("ChessPick_Block", 8410, -350, 90, 110, "Variant_Block", ("ChessPad", "None"), tags=S + ("ChessPad",))
    trig("ChessPick_Diag", 8410, 0, 90, 110, "Variant_Diag", ("ChessPad", "Gap_Diag"), tags=S + ("ChessPad",))
    trig("ChessPick_Expose", 8410, 350, 90, 110, "None", ("ChessPad", "Gap_Expose"), tags=S + ("ChessPad",))
    H = 320
    T.box("Cell_N", 9400, 9790, 380, 400, 0, H, D, "Chess/Cell", S)
    T.box("Cell_S_a", 9400, 9550, -400, -380, 0, H, D, "Chess/Cell", S); T.box("Cell_S_b", 9650, 9790, -400, -380, 0, H, D, "Chess/Cell", S)
    T.box("Cell_S_hatch", 9550, 9650, -400, -380, 0, 220, D, "Chess/Cell", S + ("Gap_Expose",)); T.box("Cell_S_lintel", 9550, 9650, -400, -380, 220, H, D, "Chess/Cell", S)
    T.box("Cell_W_a", 9400, 9420, -400, -150, 0, H, D, "Chess/Cell", S); T.box("Cell_W_b", 9400, 9420, 150, 400, 0, H, D, "Chess/Cell", S)
    T.box("Cell_W_gap", 9400, 9420, -150, 150, 0, H, D, "Chess/Cell", S + ("Gap_Diag",))
    hide(T.box("Block_Crate", 9000, 9150, 500, 650, 0, 160, G, "Chess/Block", S + ("Variant_Block",)),
         T.box("Block_Catwalk", 9450, 9790, 240, 500, 400, 420, G, "Chess/Block", S + ("Variant_Block",)))
    mover("Diag_Patrol", 9320, 0, 110, (70, 70, 200), amp=(0, 280, 0), speed=1.5, kill=200.0, tags=S + ("Variant_Diag", "FocusPause"), disabled=True, hidden=True, folder="Chess/Diag")
    mover("Expose_Shuttle", 9600, -330, 110, (100, 60, 220), amp=(170, 0, 0), speed=3.0, kill=90.0, tags=S + ("FocusPause",), m=G, folder="Chess/Expose")
    trig("Chess_Exit", 9600, 0, 100, 150, flag=4, target="M_RealRoom", tags=S)
    T.text("Chess_Hint", 8410, 0, 260, "CHOOSE A PIECE", 40.0, (0.85, 0.9, 1.0), 180.0, "Chess/Pads").tags = [unreal.Name("S40"), unreal.Name("ChessPad"), unreal.Name("TUM_Built")]
    T.LES().save_current_level(); return {"catwalk_y": cy, "top": top}

def war():
    T.LES().load_level("/Game/TUM/Maps/M_Cut_WarField"); T.clear_built()
    for a in T.EAS().get_all_level_actors():
        if "Floor" in a.get_actor_label(): T.EAS().destroy_actor(a)
    T.base_lighting(sun_pitch=-22, sun_yaw=-40, sun=1.2, sky=0.45, fog=0.05, cold=True)
    player_start(0, 0, 120); W = "War"
    T.box("Start_Floor", -300, 600, -2300, 2300, -20, 0, G, W); T.box("End_Floor", 5200, 6600, -2300, 2300, -20, 0, G, W)
    T.box("Wall_Back", -340, -300, -2300, 2300, 0, 600, D, W)
    for s, y0, y1 in (("S", -2340, -2300), ("N", 2300, 2340)): T.box(f"Wall_{s}", -300, 6600, y0, y1, 0, 600, D, W)
    T.box("Wall_End", 6600, 6640, -2300, 2300, 0, 600, D, W)
    for s, y in (("L", -800), ("R", 800)): T.box(f"LaneWall_{s}", 600, 5200, y - 30, y + 30, 0, 300, D, W)
    # left: safer cover route (zig-zag low walls, one slow rider)
    T.box("Floor_Cover", 600, 5200, -2300, -830, -20, 0, G, W)
    for i, x in enumerate((1400, 2600, 3800)):
        y0, y1 = (-2300, -1450) if i % 2 == 0 else (-1650, -830)
        T.box(f"Cover_Wall_{i}", x, x + 120, y0, y1, 0, 300, D, W)
    mover("Rider_Cover", 3200, -1550, 110, (90, 90, 210), amp=(0, 650, 0), speed=0.7, kill=200.0, m=D, folder="War/Threats")
    # middle: quick trench/wagon route, three fast crossing soldiers
    T.box("Floor_Trench", 600, 5200, -770, 770, -20, 0, G, W)
    for i, (x, y) in enumerate(((1600, -300), (2800, 300), (4000, -200))): T.box(f"Wagon_{i}", x, x + 300, y - 100, y + 100, 0, 200, D, W)
    for i, (x, sp, ph) in enumerate(((2200, 1.8, 0.0), (3400, 2.2, 1.5), (4600, 2.0, 3.0))):
        mover(f"Soldier_{i}", x, 0, 110, (80, 80, 200), amp=(0, 650, 0), speed=sp, phase=ph, kill=200.0, m=D, folder="War/Threats")
    # right: risky mud route with gaps only a Boost crosses
    for i, (x0, x1) in enumerate(((600, 1500), (2100, 3000), (3600, 4400), (5000, 5200))):
        T.box(f"Mud_{i}", x0, x1, 830, 2300, -20, 0, D, W)
    for nm, x, y in (("CP_W0", 0, 0), ("CP_L1", 650, -1550), ("CP_M1", 650, 0), ("CP_R1", 650, 1550), ("CP_L2", 2900, -1100), ("CP_M2", 2900, 0),
                     ("CP_R2", 2200, 1550), ("CP_R3", 3700, 1550), ("CP_End", 5300, 0)): cp(nm, x, y)
    # shrine: cut the marked rope to drop the silver seal, take it
    for s, y in (("S", -260), ("N", 260)): T.box(f"Shrine_Pillar_{s}", 5850, 5950, y - 50, y + 50, 0, 750, G, W)
    T.box("Shrine_Lintel", 5850, 5950, -310, 310, 750, 820, G, W)
    T.box("Rope", 5890, 5910, -10, 10, 420, 750, G, W, ("WarRope",), collide=False)
    T.box("Seal_Hanging", 5860, 5940, -40, 40, 340, 420, G, W, ("WarRope",), mesh=T.CYL)
    hide(T.box("Seal_Ground", 6060, 6140, -40, 40, 0, 20, G, W, ("SealDropped",), mesh=T.CYL))
    T.light("Shrine_Light", 5900, 0, 900, (0.85, 0.9, 1.0), 40000.0, 1500.0, W)
    trig("Rope_Cut", 5900, 0, 100, 230, "SealDropped", ("WarRope", "None"))
    trig("Seal_Take", 6100, 0, 90, 150, flag=2, target="M_FactoryHub", disabled=True, tags=("SealDropped",))
    T.LES().save_current_level(); return "ok"

def cliff():
    T.LES().load_level("/Game/TUM/Maps/M_Cut_Cliff"); T.clear_built()
    for a in T.EAS().get_all_level_actors():
        if "Floor" in a.get_actor_label(): T.EAS().destroy_actor(a)
    T.base_lighting(sun_pitch=-15, sun_yaw=-10, sun=1.6, sky=0.6, fog=0.035, cold=True)
    player_start(-200, 0, 120); C = "Cliff"
    T.box("Start_Ledge", -600, 400, -500, 500, -300, 0, D, C); T.box("Start_CliffWall", -700, -600, -900, 900, -300, 1200, D, C)
    T.box("End_Ledge", 5000, 6000, -600, 600, -300, 0, D, C)
    T.box("Mist", -3000, 9000, -6000, 6000, -2050, -2000, G, C, collide=False)
    plats = [(1000, 1400, 0), (2000, 2400, 80), (3000, 3400, 0), (4000, 4400, 120)]
    hide(*[T.box(f"Glass_{i}", x0, x1, -200, 200, z - 25, z, G, C, ("CliffPlatform",)) for i, (x0, x1, z) in enumerate(plats)])
    for s, y in (("S", -300), ("N", 300)): T.box(f"Arch_Pillar_{s}", 5450, 5550, y - 60, y + 60, 0, 700, G, C)
    lint = T.box("Arch_Lintel", 5450, 5550, -360, 360, 700, 780, G, C)
    cp("CP_C0", 0, 0); cp("CP_C1", 5200, 0)
    anchor("AlignAnchor_Reveal", 0, 0, 100, lint, reveal="CliffPlatform", reveal_time=9.0, radius=500.0, mindot=0.995, tags=("CutAnchor_Reveal",))
    T.light("Arch_Light", 5500, 0, 900, (0.8, 0.88, 1.0), 50000.0, 1800.0, C)
    trig("Cliff_Goal", 5500, 0, 100, 220, flag=3, target="M_FactoryHub")
    T.LES().save_current_level(); return "ok"

def realroom():
    T.LES().load_level("/Game/TUM/Maps/M_RealRoom"); T.clear_built()
    for a in T.EAS().get_all_level_actors():
        if "Floor" in a.get_actor_label(): T.EAS().destroy_actor(a)
    player_start(-150, 100, 120, -40.0); Rm = "Room"
    T.box("Room_Floor", -420, 420, -420, 420, -20, 0, G, Rm); T.box("Room_Ceiling", -420, 420, -420, 420, 320, 340, D, Rm)
    for nm, b in (("W", (-440, -420, -420, 420)), ("E", (420, 440, -420, 420)), ("S", (-420, 420, -440, -420)), ("N", (-420, 420, 420, 440))):
        T.box(f"Room_Wall_{nm}", *b, 0, 320, D, Rm)
    T.box("Desk", 150, 380, -380, -260, 0, 78, G, Rm); T.box("Bed", -400, -150, 150, 400, 0, 55, G, Rm)
    T.box("Window_Rain", -200, 200, 415, 420, 120, 280, G, Rm, collide=False)
    globe = T.box("Lamp_Globe", 300, 350, -345, -295, 100, 150, G, Rm, mesh=T.SPH, collide=False)
    T.light("Lamp_Light", 325, -320, 140, (1.0, 0.72, 0.4), 2500.0, 900.0, Rm)
    T.light("Room_Fill", 0, 0, 280, (0.45, 0.55, 0.75), 600.0, 900.0, Rm)
    T.box("Headphones", 200, 240, -330, -290, 78, 98, D, Rm, ("Intro",), collide=False)
    anchor("AlignAnchor_Factory", 60, -120, 100, globe, "M_FactoryHub", radius=320.0, mindot=0.985, save_return=False, tags=("CutAnchor_Factory",))
    hide(T.box("Knight_Desk", 250, 280, -300, -270, 78, 140, G, Rm, ("Ending",), collide=False))
    for i, (s, z, sz) in enumerate((("Morning.", 230, 34.0), ("THE UNFINISHED MOVE", 180, 46.0), ("Thank you for playing.", 140, 26.0))):
        t = T.text(f"Ending_Text_{i}", 400, -60, z, s, sz, (1.0, 0.86, 0.62), 180.0, "Room/Ending"); t.tags = t.tags + [unreal.Name("Ending")]; hide(t)
    T.tag(T.EAS().spawn_actor_from_class(cls(RR), V(0, 0, 200), T.R()), "RealRoomRoute", "Gameplay")
    T.LES().save_current_level(); return "ok"

def run_all(steps=("factory", "war", "cliff", "realroom")):
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    res = {"err": {}}
    for n in steps:
        try: res[n] = globals()[n]()
        except Exception: res["err"][n] = traceback.format_exc()[-1500:]
    T.LES().load_level("/Game/TUM/Maps/M_FactoryHub")
    return res
