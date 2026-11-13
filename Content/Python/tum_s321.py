# War as a battle: knights that chase you in the open (hide in the trench), artillery explosions, soldiers running across (not back and forth),
# duels that keep changing moves with clangs and shouts, battle ambience, nothing floating, no falling off the map
import unreal, importlib, traceback, math, random
import tum_graph as TG; importlib.reload(TG)
import tum_s195 as W; importlib.reload(W)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = W.E; L = W.L; V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"
GS = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Animations"
SK = unreal.SkeletalMeshActor.static_class(); AS = unreal.AnimSequence.static_class(); SB = unreal.SoundBase.static_class()
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def bp(name):
    p = f"{WB}/{name}"
    if not EAL.does_asset_exist(p): BT.create(WB, name, unreal.Actor.static_class())
    return p
def editable(p, names, defaults={}):
    b = EAL.load_asset(p)
    for n in names: BEL.set_blueprint_variable_instance_editable(b, n, True)
    BEL.compile_blueprint(b); cdo = unreal.get_default_object(b.generated_class())
    for k, v in defaults.items(): cdo.set_editor_property(k, v)
    EAL.save_loaded_asset(b, False)
g = lambda n: f"(Variables|Default|Get{n})"
def mesh(var): return f"(Class|SkeletalMeshActor|GetSkeletalMeshComponent :self {g(var)})"
def play(var, anim, loop="false"): return f"(Components|Animation|PlayAnimation :self {mesh(var)} :NewAnimToPlay {anim} :bLooping {loop})"
def pick(var, idx, n):
    s = play(var, g(f"Anim{n - 1}"))
    for i in range(n - 2, -1, -1):
        s = f"(if (== {idx} {i}) {play(var, g(f'Anim{i}'))} (else {s}))"
    return s

def sounds():
    tasks = []
    for f in ("SFX_Explosion", "SFX_SwordClang", "SFX_BattleAmbience"):
        t = unreal.AssetImportTask(); t.set_editor_property("filename", rf"C:\UnrealProjects\TheUnfinishedMove\SourceArt\audio\sfx\{f}.wav")
        t.set_editor_property("destination_path", f"{R}/Audio/SFX"); t.set_editor_property("automated", True); t.set_editor_property("save", True); t.set_editor_property("replace_existing", True)
        tasks.append(t)
    AT.import_asset_tasks(tasks)
    amb = EAL.load_asset(f"{R}/Audio/SFX/SFX_BattleAmbience"); amb.set_editor_property("looping", True); EAL.save_loaded_asset(amb, False)
    return "ok"

def runner():
    p = bp("BP_Runner"); TG.ensure_vars(p, [("Dist", "float"), ("Speed", "float"), ("Traveled", "float")])
    code = f"""
(event EventTick (DeltaSeconds)
  (bind f (Transformation|GetActorForwardVector))
  (bind step (* {g('Speed')} DeltaSeconds))
  (Transformation|AddActorWorldOffset :DeltaLocation (Math|Vector|MakeVector (* (.x f) step) (* (.y f) step) 0.0) :bTeleport true)
  (Variables|Default|SetTraveled (+ {g('Traveled')} step))
  (if (> {g('Traveled')} {g('Dist')})
    (Transformation|AddActorWorldOffset :DeltaLocation (Math|Vector|MakeVector (* (.x f) (- 0.0 {g('Traveled')})) (* (.y f) (- 0.0 {g('Traveled')})) 0.0) :bTeleport true)
    (Variables|Default|SetTraveled 0.0)))
"""
    r = TG.run(p, code, clear=True); editable(p, ["Dist", "Speed", "Traveled"], {"Dist": 4000.0, "Speed": 520.0}); return str(r)[:200]

def duel():
    p = bp("BP_DuelPair")
    TG.ensure_vars(p, [("T", "float"), ("Next", "float")] , objs=[("A", SK), ("B", SK), ("Clang", SB), ("Shout", SB)] + [(f"Anim{i}", AS) for i in range(10)])
    code = f"""
(event EventTick (DeltaSeconds)
  (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
  (if (> {g('T')} {g('Next')})
    (Variables|Default|SetT 0.0)
    (Variables|Default|SetNext (Math|Random|RandomFloatinRange :Min 0.8 :Max 1.6))
    (bind i (Math|Random|RandomIntegerinRange :Min 0 :Max 9))
    (bind j (Math|Random|RandomIntegerinRange :Min 0 :Max 9))
    {pick('A', 'i', 10)}
    {pick('B', 'j', 10)}
    (Audio|PlaySoundatLocation :Sound {g('Clang')} :Location (Transformation|GetActorLocation :self {g('A')}) :VolumeMultiplier 0.5 :PitchMultiplier (Math|Random|RandomFloatinRange :Min 0.8 :Max 1.25))
    (if (< (Math|Random|RandomFloatinRange :Min 0.0 :Max 1.0) 0.3)
      (Audio|PlaySoundatLocation :Sound {g('Shout')} :Location (Transformation|GetActorLocation :self {g('B')}) :VolumeMultiplier 0.6))))
"""
    r = TG.run(p, code, clear=True); editable(p, ["A", "B", "Clang", "Shout"] + [f"Anim{i}" for i in range(10)], {"Next": 1.0}); return str(r)[:200]

def hunter():
    p = bp("BP_Hunter")
    TG.ensure_vars(p, [("State", "int"), ("HomeX", "float"), ("HomeY", "float"), ("Chase", "float"), ("Speed", "float"), ("Sight", "float")],
                   objs=[("Body", SK), ("RunAnim", AS), ("FightAnim", AS), ("Shout", SB)])
    pl = "(Game|GetPlayerCharacter 0)"
    code = f"""
(event EventBeginPlay
  (bind l (Transformation|GetActorLocation))
  (Variables|Default|SetHomeX (.x l))
  (Variables|Default|SetHomeY (.y l))
  (Variables|Default|SetState 0))

(event EventTick (DeltaSeconds)
  (bind me (Transformation|GetActorLocation))
  (bind pp (Transformation|GetActorLocation :self {pl}))
  (bind d (Transformation|GetDistanceTo :OtherActor {pl}))
  (bind open (and (> (.y pp) -790.0) (< (.y pp) 790.0)))
  (if (== {g('State')} 0)
    (if (and open (< d {g('Sight')}))
      (Variables|Default|SetState 1)
      (Variables|Default|SetChase 0.0)
      {play('Body', g('RunAnim'), 'true')}
      (Audio|PlaySoundatLocation :Sound {g('Shout')} :Location me :VolumeMultiplier 0.9)))
  (if (== {g('State')} 1)
    (Variables|Default|SetChase (+ {g('Chase')} DeltaSeconds))
    (bind tgt (Math|Vector|MakeVector (.x pp) (.y pp) (.z me)))
    (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterptoConstant :Current me :Target tgt :DeltaTime DeltaSeconds :InterpSpeed {g('Speed')}) :bTeleport true)
    (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start me :Target tgt) :bTeleportPhysics true)
    (if (< d 130.0)
      (Variables|Default|SetState 2)
      (bind ch (Utilities|Casting|CastToBP_TUMCharacter :Object {pl})
        (:then (Class|BPTUMCharacter|Respawn :self ch))
        (:CastFailed))
      (else
        (if (or (not open) (> {g('Chase')} 7.0))
          (Variables|Default|SetState 2)))))
  (if (== {g('State')} 2)
    (bind home (Math|Vector|MakeVector {g('HomeX')} {g('HomeY')} (.z me)))
    (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterptoConstant :Current me :Target home :DeltaTime DeltaSeconds :InterpSpeed 300.0) :bTeleport true)
    (Transformation|SetActorRotation :NewRotation (Math|Rotator|FindLookatRotation :Start me :Target home) :bTeleportPhysics true)
    (if (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x me) {g('HomeX')}) (- (.y me) {g('HomeY')}) 0.0)) 20.0)
      (Variables|Default|SetState 0)
      {play('Body', g('FightAnim'), 'true')})))
"""
    r = TG.run(p, code, clear=True); editable(p, ["Body", "RunAnim", "FightAnim", "Shout", "Speed", "Sight"], {"Speed": 430.0, "Sight": 950.0}); return str(r)[:200]

def artillery():
    p = bp("BP_Artillery")
    TG.ensure_vars(p, [("T", "float"), ("Next", "float")], objs=[("Boom", SB), ("FX", unreal.ParticleSystem.static_class()), ("Smoke", unreal.NiagaraSystem.static_class())])
    pl = "(Game|GetPlayerCharacter 0)"
    code = f"""
(event EventTick (DeltaSeconds)
  (Variables|Default|SetT (+ {g('T')} DeltaSeconds))
  (if (> {g('T')} {g('Next')})
    (Variables|Default|SetT 0.0)
    (Variables|Default|SetNext (Math|Random|RandomFloatinRange :Min 2.0 :Max 4.2))
    (bind pp (Transformation|GetActorLocation :self {pl}))
    (bind loc (Math|Vector|MakeVector (+ (.x pp) (Math|Random|RandomFloatinRange :Min 300.0 :Max 1500.0)) (+ (.y pp) (Math|Random|RandomFloatinRange :Min -1100.0 :Max 1100.0)) 0.0))
    (Effects|SpawnEmitteratLocation :EmitterTemplate {g('FX')} :Location loc :Scale (Math|Vector|MakeVector 3.0 3.0 3.0))
    (Niagara|SpawnSystematLocation :SystemTemplate {g('Smoke')} :Location loc)
    (Audio|PlaySoundatLocation :Sound {g('Boom')} :Location loc :VolumeMultiplier 1.0 :PitchMultiplier (Math|Random|RandomFloatinRange :Min 0.85 :Max 1.1))
    (if (< (Math|Vector|VectorLength (Math|Vector|MakeVector (- (.x loc) (.x pp)) (- (.y loc) (.y pp)) 0.0)) 420.0)
      (bind ch (Utilities|Casting|CastToCharacter :Object {pl})
        (:then (Character|LaunchCharacter :self ch :LaunchVelocity (Math|Vector|MakeVector (* (- (.x pp) (.x loc)) 2.0) (* (- (.y pp) (.y loc)) 2.0) 520.0) :bXYOverride true :bZOverride true))
        (:CastFailed)))))
"""
    r = TG.run(p, code, clear=True); editable(p, ["Boom", "FX", "Smoke"], {"Next": 3.0}); return str(r)[:200]

def level():
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    out = {}
    for a in list(E.get_all_level_actors()):
        lab = a.get_actor_label()
        if lab.startswith(("Crowd_", "Duel_", "Runner_", "DuelPair_", "Hunter_", "Artillery", "Battle_Ambience", "Trench_")): E.destroy_actor(a)
    # old back-and-forth threats off
    for n in ("Soldier_0", "Soldier_1", "Soldier_2", "Rider_Cover"):
        m = W.find(n)
        if m:
            m.set_editor_property("KillRadius", 0.0); m.set_editor_property("bStartDisabled", True); m.set_actor_hidden_in_game(True)
            for c in m.get_attached_actors(): c.set_actor_hidden_in_game(True)
    A = lambda n: EAL.load_asset(f"{GS}/{n}")
    clang = EAL.load_asset(f"{R}/Audio/SFX/SFX_SwordClang"); boom = EAL.load_asset(f"{R}/Audio/SFX/SFX_Explosion")
    shout = EAL.load_asset("/Game/ParagonGreystone/Audio/Cues/Greystone_Effort_Attack"); cry = EAL.load_asset("/Game/ParagonGreystone/Audio/Cues/Greystone_Effort_Cheer") or shout
    fight = ["Attack_A_Fast", "Attack_B_Fast", "Attack_C_Fast", "Attack_D_Fast", "Attack_A_Med", "Attack_B_Med", "Attack_C_Med", "Deflect_InPlace", "Attack_PrimaryA", "Attack_PrimaryB"]
    random.seed(31)
    # runners: one-way across the battlefield beyond the walls, wrapping out of sight
    rcls = EAL.load_asset(f"{WB}/BP_Runner").generated_class(); n = 0
    for side in (-1, 1):
        for i in range(12):
            y = side * random.uniform(2900, 6500); fwd = random.choice((0, 180, 0)); x0 = -3000 if fwd == 0 else 9500
            x0 += random.uniform(-1500, 1500) + (random.uniform(0, 9000) * (1 if fwd == 0 else -1))
            r = E.spawn_actor_from_class(rcls, V(x0, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=fwd + random.uniform(-12, 12)))
            r.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            r.set_editor_property("Dist", 12500.0); r.set_editor_property("Speed", random.uniform(430, 600)); r.set_editor_property("Traveled", random.uniform(0, 12000))
            W.label(r, f"Runner_{n}", "Art/War/Battle")
            s = W.soldier(f"Runner_{n}_Mesh", x0, y, 4, fwd - 90, "TravelMode_Fwd", rate=random.uniform(0.9, 1.1), pos=random.uniform(0, 1), folder="Art/War/Battle", shadow=abs(y) < 4500)
            s.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=r.get_actor_rotation().yaw - 90), False)
            s.attach_to_actor(r, "", W.KW, W.KW, W.KW, False); n += 1
    out["runners"] = n
    # duels with changing moves, inside the field edges and beyond the walls
    dcls = EAL.load_asset(f"{WB}/BP_DuelPair").generated_class(); n = 0
    spots = [(x, s * random.uniform(2000, 2200)) for s in (-1, 1) for x in (900, 2000, 3000, 4000, 5000)] + \
            [(random.uniform(-1000, 7500), s * random.uniform(2800, 5000)) for s in (-1, 1) for _ in range(7)]
    for (x, y) in spots:
        yaw = random.uniform(0, 360); dx, dy = math.cos(math.radians(yaw)) * 85, math.sin(math.radians(yaw)) * 85
        a = W.soldier(f"Duel_{n}a", x - dx, y - dy, 4, yaw - 90, random.choice(fight), skin=random.choice(W.SKINS[:2]), folder="Art/War/Battle")
        b = W.soldier(f"Duel_{n}b", x + dx, y + dy, 4, yaw + 90, random.choice(fight), skin=random.choice(W.SKINS[2:]), folder="Art/War/Battle")
        for s_ in (a, b):
            d = s_.skeletal_mesh_component.get_editor_property("animation_data"); d.set_editor_property("saved_looping", False); s_.skeletal_mesh_component.set_editor_property("animation_data", d)
        c = E.spawn_actor_from_class(dcls, V(x, y, 100), unreal.Rotator())
        c.set_editor_property("A", a); c.set_editor_property("B", b); c.set_editor_property("Clang", clang); c.set_editor_property("Shout", shout)
        for i, an in enumerate(fight): c.set_editor_property(f"Anim{i}", A(an))
        W.label(c, f"DuelPair_{n}", "Art/War/Battle"); n += 1
    out["duels"] = n
    # hunters: knights in the open middle lane who chase you while you're in it
    hcls = EAL.load_asset(f"{WB}/BP_Hunter").generated_class(); n = 0
    for (x, y) in ((1700, -350), (2600, 420), (3500, -250), (4400, 330), (5100, -150)):
        h = E.spawn_actor_from_class(hcls, V(x, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=180)); h.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        body = W.soldier(f"Hunter_{n}_Mesh", x, y, 4, 90, random.choice(["Attack_A_Med", "Attack_C_Med", "Emote_Taunt_BringItOn_T1"]), skin=W.SKINS[2 + n % 2], folder="Art/War/Battle")
        body.attach_to_actor(h, "", W.KW, W.KW, W.KW, False)
        h.set_editor_property("Body", body); h.set_editor_property("RunAnim", A("TravelMode_Fwd")); h.set_editor_property("FightAnim", A("Emote_Taunt_BringItOn_T1"))
        h.set_editor_property("Shout", cry)
        W.label(h, f"Hunter_{n}", "Art/War/Battle"); n += 1
    out["hunters"] = n
    # artillery
    art = E.spawn_actor_from_class(EAL.load_asset(f"{WB}/BP_Artillery").generated_class(), V(0, 0, 0), unreal.Rotator())
    art.set_editor_property("Boom", boom)
    art.set_editor_property("FX", EAL.load_asset("/Game/ParagonGreystone/FX/Particles/Greystone/Abilities/LeapAOE/FX/P_Greystone_LeapAOE_GroundSmash"))
    art.set_editor_property("Smoke", EAL.load_asset("/Game/Effects/NS_SmokeBillow"))
    W.label(art, "Artillery", "Gameplay")
    # battle ambience
    amb = E.spawn_actor_from_class(unreal.AmbientSound, V(0, 0, 0), unreal.Rotator())
    ac = amb.get_component_by_class(unreal.AudioComponent); ac.set_editor_property("sound", EAL.load_asset(f"{R}/Audio/SFX/SFX_BattleAmbience"))
    ac.set_editor_property("allow_spatialization", False); ac.set_editor_property("volume_multiplier", 0.55)
    W.label(amb, "Battle_Ambience", "Audio")
    # the trench on the left: palisade of stakes + planked revetment along its inner edge
    stakes = W.sm(f"{W.MS}/Stakes_And_Wedges_Pack_tl2effiva/SM_Stakes_And_WedgeSM_Pack_tl2effiva_00_N1")
    beam = W.sm(f"{W.MS}/Worn_Wooden_Beam_tgmsdc0fa/SM_Worn_Wooden_Beam_tgmsdc0fa_00_N1"); n = 0
    x = 700
    while x < 5100:
        W.put(stakes, f"Trench_Stakes_{n}", x, -845 + random.uniform(-15, 15), 0, 90 + random.uniform(-6, 6), h=170, folder="Art/War/Trench")
        W.put(beam, f"Trench_Plank_{n}", x + 140, -870, 40, 0, length=300, pitch=90, folder="Art/War/Trench")
        x += random.uniform(330, 420); n += 1
    out["trench"] = n
    # ground catches falls; nothing floats
    gr = W.find("War_Ground")
    if gr: gr.set_actor_enable_collision(True); gr.static_mesh_component.set_collision_profile_name("BlockAll")
    fl = 0
    for a in E.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor) or a.get_editor_property("hidden"): continue
        f = str(a.get_folder_path()); lab = a.get_actor_label()
        if any(k in f for k in ("Shrine", "Trench")) or lab.startswith(("Seal", "Rope", "Shrine", "Horizon_", "War_", "Fire_Logs")): continue
        o, e = a.get_actor_bounds(False)
        base = 0.0 if (abs(o.y) < 2300 and -300 < o.x < 6600) else -8.0
        if 25 < (o.z - e.z) - base < 2000:
            l = a.get_actor_location(); a.set_actor_location(V(l.x, l.y, l.z - ((o.z - e.z) - base) - 4), False, False); fl += 1
    out["unfloated"] = fl
    hud = [a for a in E.get_all_level_actors() if a.get_actor_label() == "HUD_0"]
    if hud: hud[0].text_render.set_text(unreal.Text("Knights in the open will chase you - hide in the trench on the left or outrun them.  Reach the shrine, cut the rope, take the silver seal."))
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    for n, f in (("sounds", sounds), ("runner", runner), ("duel", duel), ("hunter", hunter), ("artillery", artillery)): step(n, f)
    if all(k in res["ok"] for k in ("runner", "duel", "hunter", "artillery")): step("level", level)
    return res
