# War: stony uneven ground (scanned ground relief + scattered stones), everything solid but jumpable, catapults you can read
import unreal, importlib, traceback, math, random
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
import tum_s364b as S; importlib.reload(S)
EAL = unreal.EditorAssetLibrary; E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"; MS = "/Game/MS/3D"
DC = "/Game/DerelictCorridor/Assets/Fab/Megascans/3D"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
def sms(folder):
    try: return [EAL.load_asset(p) for p in EAL.list_assets(folder, False, False) if p.split("/")[-1].startswith("SM_")]
    except Exception: return []

def catapult_bp():
    p = f"{WB}/BP_Catapult"
    TG.ensure_vars(p, [(n, "float") for n in ("T", "Next", "OX", "OY", "OZ", "TX", "TY", "TZ")] + [("Fly", "bool")],
                   objs=[("Rock", unreal.StaticMeshActor.static_class()), ("Launch", unreal.SoundBase.static_class()), ("Impact", unreal.SoundBase.static_class()),
                         ("Dust", unreal.NiagaraSystem.static_class()), ("Trail", unreal.NiagaraSystem.static_class()), ("Cat", unreal.StaticMeshActor.static_class())])
    code = f"""
(event EventTick (DeltaSeconds)
  (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
  (bind me (Transformation|GetActorLocation))
  (if {g('Fly')}
    (bind a (/ {g('T')} 2.4))
    (bind h (* (Math|Trig|Sin(Radians) (* a 3.14159)) 2600.0))
    (Transformation|SetActorLocation :self {g('Rock')} :NewLocation (Math|Vector|MakeVector (+ {g('OX')} (* (- {g('TX')} {g('OX')}) a)) (+ {g('OY')} (* (- {g('TY')} {g('OY')}) a)) (+ (+ {g('OZ')} (* (- {g('TZ')} {g('OZ')}) a)) h)) :bTeleport true)
    (Transformation|AddActorLocalRotation :self {g('Rock')} :DeltaRotation (Math|Rotator|MakeRotator :Roll (* DeltaSeconds 200.0) :Pitch (* DeltaSeconds 300.0) :Yaw 0.0))
    (if (> a 1.0)
      (Variables|Default|SetFly false)
      (Variables|Default|SetT 0.0)
      (Variables|Default|SetNext (Math|Random|RandomFloatinRange :Min 4.0 :Max 7.5))
      (bind tg (Math|Vector|MakeVector {g('TX')} {g('TY')} {g('TZ')}))
      (Transformation|SetActorLocation :self {g('Rock')} :NewLocation tg :bTeleport true)
      (Audio|PlaySoundatLocation :Sound {g('Impact')} :Location tg :VolumeMultiplier 1.3 :PitchMultiplier (Math|Random|RandomFloatinRange :Min 0.85 :Max 1.1))
      (Niagara|SpawnSystematLocation :SystemTemplate {g('Dust')} :Location tg)
      (bind pp (Transformation|GetActorLocation :self {PL}))
      (if (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x pp) {g('TX')}) (- (.y pp) {g('TY')}) 0.0)) 280.0)
        (bind ch (Utilities|Casting|CastToCharacter :Object {PL})
          (:then (Character|LaunchCharacter :self ch :LaunchVelocity (Math|Vector|MakeVector (* (- (.x pp) {g('TX')}) 1.5) (* (- (.y pp) {g('TY')}) 1.5) 280.0) :bXYOverride true :bZOverride true))
          (:CastFailed))))
    (else
      (if (> {g('T')} 1.6)
        (Transformation|SetActorLocation :self {g('Rock')} :NewLocation (Math|Vector|MakeVector (.x me) (.y me) (+ (.z me) 330.0)) :bTeleport true))
      (if (> {g('T')} {g('Next')})
        (Variables|Default|SetFly true)
        (Variables|Default|SetT 0.0)
        (bind pl (Transformation|GetActorLocation :self {PL}))
        (Variables|Default|SetTX (+ (.x pl) (Math|Random|RandomFloatinRange :Min 450.0 :Max 1500.0)))
        (Variables|Default|SetTY (+ (.y pl) (Math|Random|RandomFloatinRange :Min -800.0 :Max 800.0)))
        (Variables|Default|SetTZ 35.0)
        (Variables|Default|SetOX (.x me))
        (Variables|Default|SetOY (.y me))
        (Variables|Default|SetOZ (+ (.z me) 330.0))
        (Niagara|SpawnSystematLocation :SystemTemplate {g('Dust')} :Location me)
        (Niagara|SpawnSystemAttached :SystemTemplate {g('Trail')} :AttachToComponent (Class|StaticMeshActor|GetStaticMeshComponent :self {g('Rock')}) :bAutoDestroy true)
        (Audio|PlaySoundatLocation :Sound {g('Launch')} :Location me :VolumeMultiplier 1.0)))))
"""
    r = TG.run(p, code, clear=True)
    S.editable(p, ["Rock", "Launch", "Impact", "Dust", "Trail", "Cat", "Next"], {"Next": 4.0}); return str(r)[:300]

def jump():
    b = EAL.load_asset(f"{R}/Core/BP_TUMCharacter"); cdo = unreal.get_default_object(b.generated_class())
    cm = cdo.get_editor_property("character_movement"); cm.set_editor_property("jump_z_velocity", 610.0); cm.set_editor_property("air_control", 0.55)
    EAL.save_loaded_asset(b, False); return "jump 610"

def level():
    out = {}
    random.seed(2024)
    A = {a.get_actor_label(): a for a in E.get_all_level_actors()}
    nt = 0
    for a in E.get_all_level_actors():
        if str(a.get_folder_path()).startswith("Art/War/GroundTiles"):
            s = a.get_actor_scale3d(); o, e = a.get_actor_bounds(False); top = o.z + e.z
            a.set_actor_scale3d(V(s.x, s.y, min(s.z * 2.6, s.x))); o2, e2 = a.get_actor_bounds(False)
            l = a.get_actor_location(); a.set_actor_location(V(l.x, l.y, l.z + (top + 6) - (o2.z + e2.z)), False, False); nt += 1
    out["tiles"] = nt
    rocky = EAL.load_asset("/Game/MS/Surfaces/Rocky_Soil_Ground_vb2qdgwew/MI_Rocky_Soil_Ground_vb2qdgwew")
    if "War_Ground" in A and rocky: A["War_Ground"].static_mesh_component.set_material(0, rocky)
    obs = M.obstacles(); ns = 0
    for b in obs:
        a = b[0]; lab = a.get_actor_label(); c = a.static_mesh_component
        if lab.startswith(("Trench_Plank", "Art_Tree_Branch", "Art_Rope", "Catapult")): continue
        c.set_collision_profile_name("BlockAll"); a.set_actor_enable_collision(True); ns += 1
    out["solid"] = ns
    segs = []
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("Wander_") and not lab.endswith(("Body", "Sword")):
            try:
                p = [(a.get_editor_property(f"{k}X"), a.get_editor_property(f"{k}Y")) for k in "ABC"]
                segs += [(p[0], p[1]), (p[1], p[2]), (p[2], p[0])]
            except Exception: pass
        if lab.startswith(("Knight_", "Duel2_")) and not lab.endswith(("Body", "Sword")):
            l = a.get_actor_location(); segs.append(((l.x - 1, l.y), (l.x + 1, l.y)))
    def segd(px, py, a, b):
        ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); return math.hypot(px - ax - t * dx, py - ay - t * dy)
    stones = sms(f"{MS}/Limestone_Rocks_ubordbyda") + sms(f"{MS}/Limestone_Rubble_ubxbejwda") + sms(f"{MS}/Beach_Rock_wenobjws") + sms(f"{DC}/Forest_Scatter_Rock_Set_01") + sms(f"{MS}/Cement_Rubble_rinet")
    out["stone_kinds"] = len(stones)
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Stone_"): E.destroy_actor(a)
    n = 0; tries = 0
    while n < 900 and tries < 9000:
        tries += 1
        x = random.uniform(-500, 6600); y = random.uniform(-4300, 4300)
        size = random.choice([18, 22, 28, 35, 45, 60, 80]) * random.uniform(0.8, 1.2)
        if abs(y) < 700 and size > 30: continue
        if any(M.inside(x, y, b, size * 0.6) for b in obs): continue
        if any(segd(x, y, *s) < 70 + size for s in segs): continue
        m = random.choice(stones)
        a = E.spawn_actor_from_object(m, V(0, 0, 0), unreal.Rotator(roll=random.uniform(-15, 15), pitch=random.uniform(-15, 15), yaw=random.uniform(0, 360)))
        o, e = a.get_actor_bounds(False); s = size / max(2 * max(e.x, e.y, e.z), 1)
        a.set_actor_scale3d(V(s, s, s * random.uniform(0.6, 1.0)))
        o, e = a.get_actor_bounds(False); l = a.get_actor_location()
        a.set_actor_location(V(l.x + x - o.x, l.y + y - o.y, l.z - (o.z - e.z) - e.z * random.uniform(0.3, 0.7)), False, False)
        c = a.static_mesh_component
        if size > 40: c.set_collision_profile_name("BlockAll")
        else: c.set_collision_profile_name("NoCollision"); a.set_actor_enable_collision(False)
        c.set_cast_shadow(size > 30)
        a.set_actor_label(f"Stone_{n}"); a.set_folder_path("Art/War/Stones"); n += 1
    out["stones"] = n
    obs = M.obstacles()
    trail = EAL.load_asset("/Game/Effects/NS_Smoke"); dust = EAL.load_asset("/Game/Effects/NS_SmokeBillow")
    want = [(1500, 1, 1700), (3300, -1, 1750), (5100, 1, 1700)]
    out["cats"] = []
    for i, (wx, sg, wy) in enumerate(want):
        cat = A.get(f"Catapult_{i}"); ctl = A.get(f"Catapult_{i}_Ctl")
        if not cat or not ctl: continue
        l = cat.get_actor_location(); o, e = cat.get_actor_bounds(False); off = l.z - (o.z - e.z)
        best = None
        for t in range(2500):
            x = wx + random.uniform(-900, 900); y = sg * (wy + random.uniform(-250, 900))
            z = M.ground_z(x, y, 4000.0)
            if z is None or abs(z) > 40: continue
            if any(M.inside(x, y, b, 300) for b in obs if not b[0].get_actor_label().startswith(("Catapult", "Stone_"))): continue
            best = (x, y, z); break
        ctl.set_editor_property("Cat", cat); ctl.set_editor_property("Trail", trail); ctl.set_editor_property("Dust", dust)
        if not best: out["cats"].append("kept"); continue
        x, y, z = best
        cat.set_actor_location(V(x, y, off + z), False, False); cat.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=-90 if sg > 0 else 90), False)
        ctl.set_actor_location(V(x, y, z), False, False)
        for a in list(E.get_all_level_actors()):
            if a.get_actor_label().startswith("Stone_"):
                al = a.get_actor_location()
                if math.hypot(al.x - x, al.y - y) < 350: E.destroy_actor(a)
        out["cats"].append([round(x), round(y)])
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("catapult", catapult_bp); step("jump", jump)
    step("level", level)
    return res
