# Meshy soldier clips all face mesh +Y (measured from foot/head bones), so body yaw = facing - 90 for every clip.
# War crowd rework: soldiers run at each other, fight, one falls and stays dead, the winner runs off.
# Replaces the looping in-place duels and the wanderers. Adds corpses on the ground. Horses moved nearer the path.
import unreal, importlib, traceback, math, random, gc
import tum_s364b as S; importlib.reload(S)
import tum_graph as TG
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
E = S.E; L = S.L; M = S.M; V = unreal.Vector; WB = S.WB; g = S.g; play = S.play; PL = S.PL
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]

N = {"ops": 0}
_OC, _OK = BT.create_node, BT.connect_pins
def _gc():
    N["ops"] += 1
    if N["ops"] % 40 == 0: gc.collect(); unreal.SystemLibrary.collect_garbage()
def _c(*a): _gc(); return _OC(*a)
def _k(*a): _gc(); return _OK(*a)

def rot(var, yaw):
    return f"(Transformation|SetActorRotation :self {g(var)} :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw {yaw}) :bTeleportPhysics true)"
def loc(var, x, y, z):
    return f"(Transformation|SetActorLocation :self {g(var)} :NewLocation (Math|Vector|MakeVector {x} {y} {z}) :bTeleport true)"

def skirmish_bp():
    p = S.bp("BP_Skirmish")
    AS = S.AS; SK = S.SK
    TG.ensure_vars(p, [("State", "int")] + [(n, "float") for n in ("T", "Dur", "Speed", "EX", "EY", "ClangT", "Wake")],
                   objs=[("A", SK), ("B", SK), ("RunAnim", AS), ("FightA", AS), ("FightB", AS), ("DieAnim", AS), ("IdleAnim", AS), ("Clang", S.SB)])
    code = f"""
(event EventBeginPlay
  (Variables|Default|SetState 0)
  (Variables|Default|SetDur (Math|Random|RandomFloatinRange :Min 4.0 :Max 9.0)))

(event EventTick (DeltaSeconds)
  (bind la (Transformation|GetActorLocation :self {g('A')}))
  (bind lb (Transformation|GetActorLocation :self {g('B')}))
  (bind dx (- (.x lb) (.x la)))
  (bind dy (- (.y lb) (.y la)))
  (bind dab (Math|Vector|VectorLength (Math|Vector|MakeVector dx dy 0.0)))
  (bind yab (Math|Trig|Atan2(Degrees) dy dx))
  (if (== {g('State')} 0)
    (if (< (Transformation|GetDistanceTo :OtherActor {PL}) {g('Wake')})
      (Variables|Default|SetState 1)
      {play('A', g('RunAnim'))}
      {play('B', g('RunAnim'))}))
  (if (== {g('State')} 1)
    (bind k (/ (* {g('Speed')} DeltaSeconds) (+ dab 1.0)))
    {loc('A', "(+ (.x la) (* dx k))", "(+ (.y la) (* dy k))", "(.z la)")}
    {loc('B', "(- (.x lb) (* dx k))", "(- (.y lb) (* dy k))", "(.z lb)")}
    {rot('A', "(- yab 90.0)")}
    {rot('B', "(+ yab 90.0)")}
    (if (< dab 150.0)
      (Variables|Default|SetState 2)
      (Variables|Default|SetT 0.0)
      {play('A', g('FightA'))}
      {play('B', g('FightB'))}
      {rot('A', "(- yab 90.0)")}
      {rot('B', "(+ yab 90.0)")}))
  (if (== {g('State')} 2)
    (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
    (Variables|Default|SetClangT (- {g('ClangT')} DeltaSeconds))
    (if (< {g('ClangT')} 0.0)
      (Variables|Default|SetClangT (Math|Random|RandomFloatinRange :Min 0.6 :Max 1.4))
      (Audio|PlaySoundatLocation :Sound {g('Clang')} :Location la :VolumeMultiplier 0.6))
    (if (> {g('T')} {g('Dur')})
      (Variables|Default|SetState 3)
      {play('B', g('DieAnim'), 'false')}
      {play('A', g('RunAnim'))}
      (Variables|Default|SetEX (+ (.x la) (* (/ (- 0.0 dy) (+ dab 1.0)) 1800.0)))
      (Variables|Default|SetEY (+ (.y la) (* (/ dx (+ dab 1.0)) 1800.0)))))
  (if (== {g('State')} 3)
    (bind ex (- {g('EX')} (.x la)))
    (bind ey (- {g('EY')} (.y la)))
    (bind de (Math|Vector|VectorLength (Math|Vector|MakeVector ex ey 0.0)))
    (bind k2 (/ (* {g('Speed')} DeltaSeconds) (+ de 1.0)))
    {loc('A', "(+ (.x la) (* ex k2))", "(+ (.y la) (* ey k2))", "(.z la)")}
    {rot('A', "(- (Math|Trig|Atan2(Degrees) ey ex) 90.0)")}
    (if (< de 60.0)
      (Variables|Default|SetState 4)
      {play('A', g('IdleAnim'))}
      {rot('A', "(- (Math|Trig|Atan2(Degrees) ey ex) 90.0)")})))
"""
    r = TG.run(p, code, clear=True)
    S.editable(p, ["A", "B", "RunAnim", "FightA", "FightB", "DieAnim", "IdleAnim", "Clang", "Speed", "Wake"], {"Speed": 490.0, "Wake": 4500.0})
    return str(r)[:300]

def kill(prefixes=(), classes=()):
    n = 0
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label(); cn = a.get_class().get_name()
        if lab.startswith(prefixes) or cn in classes:
            for ch in a.get_attached_actors(): E.destroy_actor(ch); n += 1
            E.destroy_actor(a); n += 1
    return n

def level():
    random.seed(9091)
    out = {}
    # remove looping duels, wanderers, copied fighters behind the start, previous skirmishes/corpses
    for a in list(E.get_all_level_actors()):
        if a.get_class().get_name() in ("BP_DuelPair_C", "BP_Wanderer_C"):
            for k in ("A", "B", "Body"):
                try:
                    b = a.get_editor_property(k)
                    if b:
                        for ch in b.get_attached_actors(): E.destroy_actor(ch)
                        E.destroy_actor(b)
                except Exception: pass
    out["removed"] = kill(("Duel2_", "DuelPair_", "Duel_", "Wander_", "Skirm_", "Corpse_"), ("BP_DuelPair_C", "BP_Wanderer_C", "BP_Skirmish_C"))
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Behind_") and isinstance(a, unreal.SkeletalMeshActor):
            for ch in a.get_attached_actors(): E.destroy_actor(ch)
            E.destroy_actor(a)
    obs = M.obstacles()
    def clear(x0, y0, x1, y1):
        d = math.hypot(x1 - x0, y1 - y0)
        return d < 1 or M.first_hit(x0, y0, (x1 - x0) / d, (y1 - y0) / d, d, obs, 80.0) is None
    ok = lambda x, y: not any(M.inside(x, y, b, 120) for b in obs)
    scls = EAL.load_asset(f"{WB}/BP_Skirmish").generated_class()
    clang = EAL.load_asset(f"{S.R}/Audio/SFX/Sword/SFX_Clash_4") if EAL.does_asset_exist(f"{S.R}/Audio/SFX/Sword/SFX_Clash_4") else None
    FIGHT = ["Right_Hand_Sword_Slash", "Sword_Judgment", "Sword_Parry", "Sword_Parry_Backward_1", "Sword_Parry_Backward_2", "Shield_Push_Left"]
    made = 0; tries = 0; spots = []
    while made < 30 and tries < 20000:
        tries += 1
        if made < 4: mx = random.uniform(-3600, -1300); my = random.uniform(-3500, 3500)
        else: mx = random.uniform(900, 9700); my = random.choice([-1, 1]) * random.uniform(450, 4200)
        if any(math.hypot(mx - sx, my - sy) < 700 for sx, sy in spots): continue
        ang = random.uniform(0, 2 * math.pi); half = random.uniform(450, 950)
        ax, ay = mx - math.cos(ang) * half, my - math.sin(ang) * half
        bx, by = mx + math.cos(ang) * half, my + math.sin(ang) * half
        ex, ey = mx - math.sin(ang) * 1800, my + math.cos(ang) * 1800
        if made >= 4 and not (ok(ax, ay) and ok(bx, by) and ok(mx, my) and clear(ax, ay, bx, by)): continue
        if made >= 4 and not (-800 < ex < 9900 and abs(ey) < 4500): continue
        yaw = math.degrees(ang)
        a_ = S.soldier(f"Skirm_{made}_A", ax, ay, 2, 0, "CrouchLookAroundBow", "Art/War/Battle/Skirmish")
        b_ = S.soldier(f"Skirm_{made}_B", bx, by, 2, 0, "CrouchLookAroundBow", "Art/War/Battle/Skirmish", sword=random.random() < 0.8)
        a_.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=yaw - 90), False); b_.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=yaw + 90), False)
        c = E.spawn_actor_from_class(scls, V(mx, my, 100), unreal.Rotator())
        c.set_editor_property("A", a_); c.set_editor_property("B", b_)
        c.set_editor_property("RunAnim", S.A(random.choice(["RunFast", "Running"])))
        c.set_editor_property("FightA", S.A(random.choice(FIGHT))); c.set_editor_property("FightB", S.A(random.choice(FIGHT)))
        c.set_editor_property("DieAnim", S.A("dying_backwards")); c.set_editor_property("IdleAnim", S.A(random.choice(["CrouchLookAroundBow", "Sword_Shout"])))
        if clang: c.set_editor_property("Clang", clang)
        c.set_editor_property("Speed", random.uniform(470.0, 500.0)); c.set_editor_property("Wake", random.uniform(3000.0, 5200.0))
        c.set_actor_label(f"Skirm_{made}"); c.set_folder_path("Art/War/Battle/Skirmish")
        spots.append((mx, my)); made += 1
    out["skirmishes"] = made
    # corpses: lying at the end of the fall, not animated
    die = S.A("dying_backwards"); length = die.get_play_length()
    n = 0; tries = 0
    while n < 34 and tries < 5000:
        tries += 1
        x = random.uniform(-3000, 9800); y = random.uniform(-4300, 4300)
        if abs(y) < 250 and x < 1500: continue
        if not ok(x, y): continue
        a = S.soldier(f"Corpse_{n}", x, y, 2, random.uniform(0, 360), "dying_backwards", "Art/War/Battle/Corpses", sword=False, pos=length)
        cm = a.skeletal_mesh_component; d = cm.get_editor_property("animation_data")
        d.set_editor_property("saved_position", length); d.set_editor_property("saved_playing", False); d.set_editor_property("saved_looping", False)
        cm.set_editor_property("animation_data", d); n += 1
        if random.random() < 0.5:
            w = E.spawn_actor_from_object(EAL.load_asset(S.SWORD), V(x + random.uniform(-90, 90), y + random.uniform(-90, 90), 6), unreal.Rotator(roll=90, pitch=0, yaw=random.uniform(0, 360)))
            w.static_mesh_component.set_collision_profile_name("NoCollision"); w.set_actor_label(f"Corpse_{n}_Sword"); w.set_folder_path("Art/War/Battle/Corpses")
    out["corpses"] = n
    # horses nearer the path so they are seen
    spots = [(2200, -1700), (3600, 1800), (5000, -1900), (6400, 1700), (7800, -1800), (9000, 1900), (1300, 2000)]
    i = 0
    for a in E.get_all_level_actors():
        if a.get_class().get_name() == "BP_Cavalry_C" and i < len(spots):
            x, y = spots[i]; l = a.get_actor_location(); a.set_actor_location(V(x, y, l.z), False, False); i += 1
    out["horses_moved"] = i
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_WarField")
    BT.create_node = _c; BT.connect_pins = _k
    try: step("bp", skirmish_bp)
    finally: BT.create_node = _OC; BT.connect_pins = _OK
    if not res["err"]: step("level", level)
    res["ops"] = N["ops"]; return res

def run_level():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_WarField"); step("level", level); return res
