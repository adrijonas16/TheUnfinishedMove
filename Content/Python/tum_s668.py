# War: soldiers at eye level (camera eye 1.52 m, soldiers x1.15 because their run/fight poses are crouched), 12 knights in the middle lane.
import unreal, importlib, traceback, math, random
import tum_s663 as F; importlib.reload(F)
import tum_s364b as S
import tum_s335 as M
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
SC = 1.15
def soldiers():
    random.seed(21); n = 0
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.SkeletalMeshActor) and not a.get_actor_label().startswith(("Cavalry_", "Corpse_")):
            m = a.skeletal_mesh_component.get_skeletal_mesh_asset()
            if m and "/War/Soldiers/" in m.get_path_name():
                s = SC * random.uniform(0.98, 1.02); a.set_actor_scale3d(V(s, s, s)); n += 1
    return n
def knights_mid():
    random.seed(909)
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("KnightMid_"):
            for ch in a.get_attached_actors(): E.destroy_actor(ch)
            E.destroy_actor(a)
    obs = M.obstacles()
    kcls = EAL.load_asset(f"{WB}/BP_Knight").generated_class(); made = 0; tries = 0; ks = []
    clashes = [EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Clash_{i}") for i in range(1, 11)]; swing = EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Swing_2")
    tmpl = [a for a in E.get_all_level_actors() if a.get_class().get_name() == "BP_Knight_C"]
    while made < 12 and tries < 8000:
        tries += 1
        x = random.uniform(1500, 9000); y = random.uniform(-620, 620)
        if any(M.inside(x, y, b, 110) for b in obs) or any(math.hypot(x - kx, y - ky) < 520 for kx, ky in ks): continue
        ks.append((x, y))
        k = E.spawn_actor_from_class(kcls, V(x, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360))); k.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        body = S.soldier(f"KnightMid_{made}_Body", x, y, 2, 180, "Walking", "Art/War/Battle/Knights"); body.set_actor_scale3d(V(SC, SC, SC))
        body.attach_to_actor(k, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        body.root_component.set_relative_rotation(unreal.Rotator(roll=0, pitch=0, yaw=-90), False, False)
        for kk, vv in (("Body", body), ("RunAnim", S.A("RunFast")), ("IdleAnim", S.A("Sword_Parry")), ("WalkAnim", S.A("Walking")), ("HitAnim", S.A("Right_Hand_Sword_Slash")), ("DieAnim", S.A("dying_backwards")), ("ReactAnim", S.A("Face_Punch_Reaction"))):
            k.set_editor_property(kk, vv)
        k.set_editor_property("Clang", random.choice(clashes)); k.set_editor_property("Shout", swing)
        if tmpl:
            for pn in ("Speed", "Sight"): k.set_editor_property(pn, tmpl[0].get_editor_property(pn))
        k.tags = [unreal.Name("Knight")]; k.set_actor_label(f"KnightMid_{made}"); k.set_folder_path("Art/War/Battle/Knights"); made += 1
    # swords of the new bodies: same grip transform as an existing knight sword
    ref = None
    for a in E.get_all_level_actors():
        if a.get_actor_label().startswith("Knight_") and a.get_actor_label().endswith("_Sword"): ref = a; break
    if ref:
        rr = ref.root_component.get_editor_property("relative_rotation"); rl = ref.root_component.get_editor_property("relative_location")
        for a in E.get_all_level_actors():
            if a.get_actor_label().startswith("KnightMid_") and a.get_actor_label().endswith("_Sword"):
                a.root_component.set_relative_rotation(rr, False, False); a.root_component.set_relative_location(rl, False, False)
    return made
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    F.EYE = 62.0
    step("camera", F.camera); step("headbob", F.headbob)
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("soldiers", soldiers); step("knights_mid", knights_mid)
    L.save_current_level(); res["probe"] = F.probe(); return res
