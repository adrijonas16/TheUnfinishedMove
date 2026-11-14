# War: (measured with an automated Play test: rocks DO fall; horses never found a clear straight line to the player
# because the field is full of walls.)
# 1) Horse lanes: clear gallop corridors (>= 25 m, box-swept against the real collision) are precomputed and stored as
#    markers; each horse picks a lane that passes near you, runs it end to end and leaves. No more idle horses.
# 2) Soldiers: only ~14 chasers (one uniform), everyone else is in a fight: 16 new pairs already fighting, 8 of them
#    in the middle lane. Fight pairs are always uniform A vs uniform B.
import unreal, importlib, traceback, math, random
import tum_s666 as Q; importlib.reload(Q)
import tum_s364b as S
import tum_s335 as M
import tum_graph as TG
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"; g = Q.g; s = Q.s; rnd = Q.rnd; vec = Q.vec; clamp = Q.clamp
SC = 1.15; ENEMY = S.MESHES[0]; ALLY = S.MESHES[1]
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
def expr_at(t, i):
    d = 0
    for j in range(i, len(t)):
        d += (t[j] == "(") - (t[j] == ")")
        if d == 0: return t[i:j + 1]

# ---------------- lanes ----------------
def lanes():
    random.seed(77)
    world = unreal.EditorLevelLibrary.get_editor_world()
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("HorseLane_"): E.destroy_actor(a)
    def clear(x0, y0, dx, dy, ln, yaw):
        r = unreal.SystemLibrary.box_trace_single(world, V(x0, y0, 129), V(x0 + dx * ln, y0 + dy * ln, 129), V(70, 75, 80), unreal.Rotator(roll=0, pitch=0, yaw=yaw),
                                                  unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        t = r.to_tuple() if r else None
        return not (t and t[0])
    mid, other = [], []
    x = -600.0
    while x <= 9800:
        y = -4200.0
        while y <= 4200:
            for k in range(12):
                yaw = k * 30.0 + random.uniform(-10, 10); dx, dy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
                for ln in (4500.0, 3500.0, 2600.0):
                    ex, ey = x + dx * ln, y + dy * ln
                    if not (-700 <= ex <= 9900 and -4300 <= ey <= 4300): continue
                    if clear(x, y, dx, dy, ln, yaw):
                        pts = [(x + dx * ln * i / 8, y + dy * ln * i / 8) for i in range(9)]
                        (mid if any(abs(py) < 700 and 0 < px < 9500 for px, py in pts) else other).append((x, y, yaw, ln))
                        break
            y += 350
        x += 350
    random.shuffle(mid); random.shuffle(other)
    pick = mid[:120] + other[:70]
    for i, (x, y, yaw, ln) in enumerate(pick):
        t = E.spawn_actor_from_class(unreal.TargetPoint, V(x, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
        t.set_actor_scale3d(V(ln / 1000.0, 1, 1)); t.tags = [unreal.Name("HorseLane")]; t.set_actor_label(f"HorseLane_{i}"); t.set_folder_path("Gameplay/HorseLanes")
    return {"mid_found": len(mid), "other_found": len(other), "placed": len(pick)}

# ---------------- cavalry ----------------
def cavalry_code():
    code = Q.cavalry_code()
    i = code.index("(if (< (Variables|Default|GetWait) 0.0)"); old = expr_at(code, i)
    yaw = Q.YAW
    new = f"""(if (< {g('Wait')} 0.0)
      {s('Best', 1000000.0)}
      (for ln (Actor|GetAllActorswithTag :Tag "HorseLane")
        (bind ll (Transformation|GetActorLocation :self ln))
        (bind fw (Transformation|GetActorForwardVector :self ln))
        (bind len (* (.x (Transformation|GetActorScale3D :self ln)) 1000.0))
        (bind tt {clamp("(+ (* (- (.x pl) (.x ll)) (.x fw)) (* (- (.y pl) (.y ll)) (.y fw)))", 0.0, "len")})
        (bind dist (Math|Vector|VectorLength {vec("(- (.x pl) (+ (.x ll) (* (.x fw) tt)))", "(- (.y pl) (+ (.y ll) (* (.y fw) tt)))", 0.0)}))
        (if (< (+ dist {rnd(0.0, 900.0)}) {g('Best')})
          {s('Best', 'dist')}
          {s('Len', 'len')}
          (if (> tt (* len 0.5))
            {s('SX', '(.x ll)')}
            {s('SY', '(.y ll)')}
            {s('DX', '(.x fw)')}
            {s('DY', '(.y fw)')}
            (else
              {s('SX', '(+ (.x ll) (* (.x fw) len))')}
              {s('SY', '(+ (.y ll) (* (.y fw) len))')}
              {s('DX', '(- 0.0 (.x fw))')}
              {s('DY', '(- 0.0 (.y fw))')}))))
      (if (< {g('Best')} 2600.0)
        {s('State', 1)}
        {s('Run', 0.0)}
        {s('Hit', 'false')}
        (Transformation|SetActorLocationAndRotation :NewLocation {vec(g('SX'), g('SY'), g('GZ'))} :NewRotation {yaw} :bTeleport true)
        (Audio|PlaySoundatLocation :Sound {g('Hoof')} :Location {vec(g('SX'), g('SY'), g('GZ'))} :VolumeMultiplier 1.2 :PitchMultiplier 0.7)
        (else
          {s('Wait', rnd(0.6, 1.5))})))"""
    code = code[:i] + new + code[i + len(old):]
    assert TG.balance(code) == 0
    return code
def cavalry():
    p = f"{WB}/BP_Cavalry"
    TG.ensure_vars(p, [("Best", "float")])
    code = cavalry_code()
    return Q.patched(lambda: str(TG.run(p, code, events=["KnockDown"], clear=True))[:300])

# ---------------- soldiers ----------------
def kill(a):
    for ch in a.get_attached_actors():
        for c2 in ch.get_attached_actors(): E.destroy_actor(c2)
        E.destroy_actor(ch)
    E.destroy_actor(a)
def setmesh(b, path):
    if b: b.skeletal_mesh_component.set_skeletal_mesh_asset(EAL.load_asset(path))
def soldiers():
    random.seed(1234); out = {}
    ks = [a for a in E.get_all_level_actors() if a.get_class().get_name() == "BP_Knight_C"]
    ks.sort(key=lambda a: abs(a.get_actor_location().y)); keep = []; freed = []
    for a in ks:
        l = a.get_actor_location()
        if len(keep) < 14 and all((k.get_actor_location() - l).length() > 650 for k in keep) and math.hypot(l.x, l.y) > 1800: keep.append(a)
        else: freed.append((l.x, l.y)); kill(a)
    for a in keep:
        setmesh(a.get_editor_property("Body"), ENEMY); a.set_editor_property("Sight", 1700.0)
    out["chasers"] = len(keep); out["removed_walkers"] = len(freed)
    sk = [a for a in E.get_all_level_actors() if a.get_class().get_name() == "BP_Skirmish_C"]
    for a in sk: setmesh(a.get_editor_property("A"), ENEMY); setmesh(a.get_editor_property("B"), ALLY)
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith("Cavalry_") and a.get_actor_label().endswith("_Rider"): setmesh(a, ENEMY)
    # new pairs, already fighting
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Fight_"): kill(a) if a.get_class().get_name() == "BP_Skirmish_C" else None
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Fight_"): E.destroy_actor(a)
    obs = M.obstacles(); ok = lambda x, y: not any(M.inside(x, y, b, 130) for b in obs)
    scls = EAL.load_asset(f"{WB}/BP_Skirmish").generated_class()
    clang = EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Clash_4")
    FIGHT = ["Right_Hand_Sword_Slash", "Sword_Judgment", "Sword_Parry", "Sword_Parry_Backward_1", "Sword_Parry_Backward_2", "Shield_Push_Left"]
    spots = []; tries = 0
    while len(spots) < 8 and tries < 4000:
        tries += 1; x = random.uniform(1300, 9000); y = random.uniform(-600, 600)
        if ok(x, y) and all(math.hypot(x - a, y - b) > 700 for a, b in spots): spots.append((x, y))
    random.shuffle(freed)
    for (x, y) in freed:
        if len(spots) >= 16: break
        if ok(x, y) and all(math.hypot(x - a, y - b) > 700 for a, b in spots): spots.append((x, y))
    ref = next((a for a in E.get_all_level_actors() if a.get_actor_label().startswith("Skirm_") and a.get_actor_label().endswith("_Sword")), None)
    for i, (mx, my) in enumerate(spots):
        ang = random.uniform(0, 2 * math.pi); yaw = math.degrees(ang); dx, dy = math.cos(ang) * 70, math.sin(ang) * 70
        fa, fb = random.choice(FIGHT), random.choice(FIGHT)
        a_ = S.soldier(f"Fight_{i}_A", mx - dx, my - dy, 2, 0, fa, "Art/War/Battle/Fights"); b_ = S.soldier(f"Fight_{i}_B", mx + dx, my + dy, 2, 0, fb, "Art/War/Battle/Fights")
        setmesh(a_, ENEMY); setmesh(b_, ALLY)
        a_.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=yaw - 90), False); b_.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=yaw + 90), False)
        for b in (a_, b_): b.set_actor_scale3d(V(SC, SC, SC))
        c = E.spawn_actor_from_class(scls, V(mx, my, 100), unreal.Rotator())
        c.set_editor_property("A", a_); c.set_editor_property("B", b_)
        c.set_editor_property("RunAnim", S.A("RunFast")); c.set_editor_property("FightA", S.A(fa)); c.set_editor_property("FightB", S.A(fb))
        c.set_editor_property("DieAnim", S.A("dying_backwards")); c.set_editor_property("IdleAnim", S.A("Sword_Shout"))
        if clang: c.set_editor_property("Clang", clang)
        c.set_editor_property("Speed", 480.0); c.set_editor_property("Wake", 1500.0); c.set_editor_property("Drop", 8.0 * SC)
        c.set_actor_label(f"Fight_{i}"); c.set_folder_path("Art/War/Battle/Fights")
    if ref:
        rr = ref.root_component.get_editor_property("relative_rotation"); rl = ref.root_component.get_editor_property("relative_location")
        for a in E.get_all_level_actors():
            if a.get_actor_label().startswith("Fight_") and a.get_actor_label().endswith("_Sword"):
                a.root_component.set_relative_rotation(rr, False, False); a.root_component.set_relative_location(rl, False, False)
    out["fight_pairs"] = len(spots); out["skirmishes"] = len(sk)
    return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("cavalry", cavalry)
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("lanes", lanes); step("soldiers", soldiers)
    L.save_current_level(); return res
