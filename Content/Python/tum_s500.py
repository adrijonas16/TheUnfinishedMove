# War, harder: sprint on SHIFT, sword attack on right mouse, Cut Boost on Q; knights take hits (2 = down), are faster/see farther,
# there are many more of them, spread over a bigger field.
import unreal, importlib, traceback, inspect, random, math
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
import tum_s364b as S; importlib.reload(S)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"
CH = f"{R}/Core/BP_TUMCharacter"; GA = f"{R}/Characters/Gael/Anim"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
FIELD = dict(x0=-900, x1=10100, y0=-4700, y1=4700)

def ia(name, keys):
    p = f"{R}/Core/{name}"
    a = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(name, f"{R}/Core", unreal.InputAction, unreal.InputAction_Factory())
    EAL.save_loaded_asset(a); return a

def inputs():
    imc = EAL.load_asset("/Game/Input/IMC_Default")
    sprint = ia("IA_Sprint", None); attack = ia("IA_Attack", None); boost = EAL.load_asset(f"{R}/Core/IA_Boost")
    data = imc.get_editor_property("default_key_mappings")
    maps = [m for m in data.get_editor_property("mappings") if m.get_editor_property("action") not in (sprint, attack, boost)]
    for act, keys in ((sprint, ("LeftShift", "Gamepad_LeftThumbstick")), (attack, ("RightMouseButton", "Gamepad_RightTrigger")), (boost, ("Q", "Gamepad_RightShoulder"))):
        for key in keys:
            k = unreal.Key(); k.set_editor_property("key_name", key)
            m = unreal.EnhancedActionKeyMapping(); m.set_editor_property("action", act); m.set_editor_property("key", k); maps.append(m)
    data.set_editor_property("mappings", maps); imc.set_editor_property("default_key_mappings", data); EAL.save_loaded_asset(imc, False)
    return "ok"

def retarget():
    rt = EAL.load_asset(f"{R}/Characters/Retarget/RTG_SoldierToQuinn")
    src = EAL.load_asset(f"{WB}/Soldiers/Anim/soldier3"); tgt = EAL.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple")
    names = ["Right_Hand_Sword_Slash"]
    for n in names:
        if EAL.does_asset_exist(f"{GA}/Q_{n}"): EAL.delete_asset(f"{GA}/Q_{n}")
    ads = [EAL.find_asset_data(f"{WB}/Soldiers/Anim/soldier3{n}") for n in names]
    r = unreal.IKRetargetBatchOperation.duplicate_and_retarget(ads, src, tgt, rt, "soldier3", "Q_", "", "", GA, False, False, True)
    return [str(a.package_name) for a in r]

def sword():
    bp = EAL.load_asset(CH)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    handles = sds.k2_gather_subobject_data_for_blueprint(bp)
    F = unreal.SubobjectDataBlueprintFunctionLibrary
    names = {}
    for h in handles:
        d = F.get_data(h); o = F.get_object(d)
        names[str(F.get_variable_name(d))] = (h, o)
    if "Sword" in names: return "exists"
    mesh_h = [h for n, (h, o) in names.items() if isinstance(o, unreal.SkeletalMeshComponent)][0]
    p = unreal.AddNewSubobjectParams(parent_handle=mesh_h, new_class=unreal.StaticMeshComponent, blueprint_context=bp)
    nh, fail = sds.add_new_subobject(p)
    sds.rename_subobject(nh, unreal.Text("Sword"))
    comp = F.get_object(F.get_data(nh))
    comp.set_editor_property("static_mesh", EAL.load_asset(S.SWORD)); comp.set_editor_property("attach_socket_name", "hand_r")
    comp.set_editor_property("relative_rotation", unreal.Rotator(roll=180, pitch=0, yaw=90)); comp.set_editor_property("relative_location", V(0, 0, 0.4))
    comp.set_collision_profile_name("NoCollision"); comp.set_editor_property("cast_shadow", True)
    BEL.compile_blueprint(bp); EAL.save_loaded_asset(bp, False)
    return str(fail)

def combat():
    TG.ensure_vars(CH, [("bAttacking", "bool")], objs=[("AttackAnim", unreal.AnimSequence.static_class()), ("SwingSfx", unreal.SoundBase.static_class()), ("HitSfx", unreal.SoundBase.static_class())])
    b = EAL.load_asset(CH); g_ = unreal.BlueprintEditorLibrary.find_event_graph(b)
    have = [BT._get_node_info(n).type_id for n in BT.find_nodes(g_)]
    if any("IA_Sprint" in t or "IA_Attack" in t for t in have): return "already wired"
    for n in list(BT.find_nodes(g_)):
        t = BT._get_node_info(n).type_id
        if any(k in t for k in ("DoSprint", "StopSprint", "DoAttack")): BT.delete_node(n)
    code = f"""
(event Custom|DoSprint
  (Class|CharacterMovementComponent|SetMaxWalkSpeed :self (Variables|Character|GetCharacterMovement) :MaxWalkSpeed 720.0))

(event Custom|StopSprint
  (Class|CharacterMovementComponent|SetMaxWalkSpeed :self (Variables|Character|GetCharacterMovement) :MaxWalkSpeed 430.0))

(event Custom|DoAttack
  (if (not (Variables|Default|GetAttacking))
    (Variables|Default|SetAttacking true)
    (if (Variables|Character|GetIsCrouched) (Character|UnCrouch))
    (Components|Animation|PlayAnimation :self (Variables|Character|GetMesh) :NewAnimToPlay (Variables|Default|GetAttackAnim) :bLooping false)
    (Audio|PlaySoundatLocation :Sound (Variables|Default|GetSwingSfx) :Location (Transformation|GetActorLocation) :VolumeMultiplier 0.7 :PitchMultiplier (Math|Random|RandomFloatinRange :Min 0.9 :Max 1.1))
    (Utilities|FlowControl|Delay 0.3)
    (bind me (Transformation|GetActorLocation))
    (bind fw (Transformation|GetActorForwardVector))
    (for k (Actor|GetAllActorswithTag :Tag "Knight")
      (bind kl (Transformation|GetActorLocation :self k))
      (bind dx (- (.x kl) (.x me)))
      (bind dy (- (.y kl) (.y me)))
      (bind dd (Math|Vector|VectorLength (Math|Vector|MakeVector dx dy 0.0)))
      (if (and (< dd 260.0) (> (+ (* (.x fw) dx) (* (.y fw) dy)) (* dd 0.25)))
        (Audio|PlaySoundatLocation :Sound (Variables|Default|GetHitSfx) :Location kl :VolumeMultiplier 1.0)
        (bind kn (Utilities|Casting|CastToBP_Knight :Object k)
          (:then (Class|BPKnight|SetHits :self kn :Hits (+ (Class|BPKnight|GetHits :self kn) 1)))
          (:CastFailed))))
    (Utilities|FlowControl|Delay 0.45)
    (Components|Animation|SetAnimationMode :self (Variables|Character|GetMesh) :InAnimationMode "AnimationBlueprint")
    (Variables|Default|SetAttacking false)))
"""
    r = TG.run(CH, code, events=["DoSprint", "StopSprint", "DoAttack"],
               binds=[("IA_Sprint", [("Started", "DoSprint"), ("Completed", "StopSprint")]), ("IA_Attack", [("Started", "DoAttack")])], clear=False)
    b = EAL.load_asset(CH); cdo = unreal.get_default_object(b.generated_class())
    cm = cdo.get_editor_property("character_movement"); cm.set_editor_property("max_walk_speed", 430.0)
    cdo.set_editor_property("AttackAnim", EAL.load_asset(f"{GA}/Q_Right_Hand_Sword_Slash"))
    cdo.set_editor_property("SwingSfx", EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Swing_3")); cdo.set_editor_property("HitSfx", EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Clash_4"))
    EAL.save_loaded_asset(b, False)
    return str(r)[:200]

def knight_bp():
    import tum_s394 as K; importlib.reload(K)
    TG.ensure_vars(f"{WB}/BP_Knight", [("Hits", "int"), ("SeenHits", "int")], objs=[("ReactAnim", unreal.AnimSequence.static_class())])
    src = inspect.getsource(K.knight)
    reps = [
        ("(Utilities|Casting|CastToCharacter :Object {PL})", "(Utilities|Casting|CastToBP_TUMCharacter :Object {PL})"),
        (":bXYOverride true :bZOverride true))\n            (:CastFailed)",
         ":bXYOverride true :bZOverride true)\n              (Class|BPTUMCharacter|SetHealth :self ch :Health (- (Class|BPTUMCharacter|GetHealth :self ch) 15.0))\n              (Class|BPTUMCharacter|SetLastHit :self ch :LastHit (Utilities|Time|GetGameTimeinSeconds)))\n            (:CastFailed)"),
        ("(if (and los (< d {g('Sight')}))", "(if (and los (< d (* {g('Sight')} (select (Class|Character|GetIsCrouched :self {PL}) 0.55 1.0))))"),
        ("(Variables|Default|SetCool 2.5)", "(Variables|Default|SetCool 1.9)"),
        ("(Variables|Default|SetShoutT (- {g('ShoutT')} DeltaSeconds))",
         """(Variables|Default|SetShoutT (- {g('ShoutT')} DeltaSeconds))
  (if (and (> {g('Hits')} {g('SeenHits')}) (not (== {g('State')} 3)))
    (Variables|Default|SetSeenHits {g('Hits')})
    (if (> {g('Hits')} 1)
      (Variables|Default|SetState 3)
      {play('Body', g('DieAnim'), 'false')}
      (else
        (Variables|Default|SetState 4)
        (Variables|Default|SetCool 0.9)
        {play('Body', g('ReactAnim'), 'false')})))"""),
    ]
    for a, b_ in reps:
        assert src.count(a) == 1, a[:60]
        src = src.replace(a, b_)
    ns = dict(K.__dict__); exec(src, ns); r = ns["knight"]()
    p = f"{WB}/BP_Knight"; bp = EAL.load_asset(p); BEL.set_blueprint_variable_instance_editable(bp, "ReactAnim", True); BEL.compile_blueprint(bp)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("Speed", 430.0); cdo.set_editor_property("Sight", 1350.0); cdo.set_editor_property("ReactAnim", S.A("Face_Punch_Reaction"))
    EAL.save_loaded_asset(bp, False); return r

def knights_level(n=22):
    random.seed(777)
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("Knight_"): E.destroy_actor(a)
    obs = M.obstacles()
    kcls = EAL.load_asset(f"{WB}/BP_Knight").generated_class(); made = 0; tries = 0; ks = []
    clashes = [EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Clash_{i}") for i in range(1, 11)]
    swing = EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Swing_2")
    while made < n and tries < 8000:
        tries += 1
        x = random.uniform(800, FIELD["x1"] - 900); y = random.uniform(FIELD["y0"] + 700, FIELD["y1"] - 700)
        if math.hypot(x, y) < 2600: continue
        if any(M.inside(x, y, b, 150) for b in obs) or any(math.hypot(x - kx, y - ky) < 950 for kx, ky in ks): continue
        z = M.ground_z(x, y) or 0.0
        ks.append((x, y))
        k = E.spawn_actor_from_class(kcls, V(x, y, z), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360))); k.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        body = S.soldier(f"Knight_{made}_Body", x, y, z + 2, 180, "Walking", "Art/War/Battle/Knights")
        body.attach_to_actor(k, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        for kk, vv in (("Body", body), ("RunAnim", S.A("RunFast")), ("IdleAnim", S.A("Sword_Parry")), ("WalkAnim", S.A("Walking")), ("HitAnim", S.A("Right_Hand_Sword_Slash")), ("DieAnim", S.A("dying_backwards")), ("ReactAnim", S.A("Face_Punch_Reaction"))):
            k.set_editor_property(kk, vv)
        k.set_editor_property("Clang", random.choice(clashes)); k.set_editor_property("Shout", swing)
        k.tags = [unreal.Name("Knight")]
        k.set_actor_label(f"Knight_{made}"); k.set_folder_path("Art/War/Battle/Knights"); made += 1
    return made

def run_a():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("TMP_"): E.destroy_actor(a)
    step("inputs", inputs); step("retarget", retarget); step("sword", sword); step("knight_bp", knight_bp); step("combat", combat)
    return res

def run_c():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("knight_bp", knight_bp); step("knights", knights_level); L.save_current_level()
    return res
