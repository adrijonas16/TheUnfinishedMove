# War pass 3:
# - horses that hit an obstacle swerve 90 deg left/right and keep galloping (up to 3 swerves) instead of freezing
# - brick/ruin walls get an invisible top so they cannot be climbed; wooden props collide with their real shape (no padding)
# - soldiers scaled to the player's height; swords set into the fist (measured from the hand/finger bones)
# - more knights in the far half of the field
# - goal: no light beam; the silver seal itself glows (unlit amber) with a small warm light
import unreal, importlib, traceback, math, random, re
import tum_s637 as H; importlib.reload(H)
import tum_s364b as S
import tum_graph as TG
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; MEL = unreal.MaterialEditingLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; WB = f"{R}/War"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]

# ---------------- horses: swerve ----------------
def bump_transform(code):
    m = re.search(r"\(if \(or \(or (th\d+) \(> \(Variables\|Default\|GetRun\) 7500\.0\)\)", code)
    if not m: raise RuntimeError("stop-if not found")
    i = m.start(); orig = H.expr_at(code, i); th = m.group(1)
    G = lambda n: f"(Variables|Default|Get{n})"
    new = f"""(if (and {th} (< {G('Bumps')} 3))
      (Variables|Default|SetBumps (+ {G('Bumps')} 1))
      (bind sgn (select (Math|Random|RandomBool) 1.0 -1.0))
      (bind ndx (* (- 0.0 {G('DY')}) sgn))
      (bind ndy (* {G('DX')} sgn))
      (Variables|Default|SetDX ndx)
      (Variables|Default|SetDY ndy)
      (Variables|Default|SetTX (+ (.x me) (* ndx 1800.0)))
      (Variables|Default|SetTY (+ (.y me) (* ndy 1800.0)))
      (Variables|Default|SetRun (* {G('Run')} 0.6))
      (Transformation|SetActorRotation :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (Math|Trig|Atan2(Degrees) ndy ndx)) :bTeleportPhysics true)
      (else
      {orig}))"""
    code = code[:i] + new + code[i + len(orig):]
    if code.count("(Variables|Default|SetHit false)") != 1: raise RuntimeError("SetHit false count")
    code = code.replace("(Variables|Default|SetHit false)", "(Variables|Default|SetHit false)\n      (Variables|Default|SetBumps 0)")
    return code
_old_hoist = H.hoist
def hoist2(code):
    code, n = _old_hoist(code)
    if "GetRun) 7500.0" in code: code = bump_transform(code); res["bump"] = True
    return code, n
def horses():
    TG.ensure_vars(f"{WB}/BP_Cavalry", [("Bumps", "int")])
    H.hoist = hoist2
    from editor_toolset.toolsets import blueprint_dsl
    blueprint_dsl.Transpiler.transpile = H.wrapped
    try: return H.C632.run()
    finally: blueprint_dsl.Transpiler.transpile = H.TRUE_ORIG; H.hoist = _old_hoist

# ---------------- level fixes ----------------
WALLS = ("Brick_Walls", "Ruins_Wall", "ChurchRuin")
WOOD = ("Wooden_Beam", "Wooden_Crate", "Wooden_Barrel", "Plank", "Stakes")
def walls_and_wood():
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith("WallTop_"): E.destroy_actor(a)
    cube = EAL.load_asset("/Engine/BasicShapes/Cube"); inv = EAL.load_asset(f"{R}/Materials/Surfaces/M_Invisible")
    out = {"tops": 0, "wood_meshes": []}
    for a in list(E.get_all_level_actors()):
        if not isinstance(a, unreal.StaticMeshActor) or a.is_hidden_ed(): continue
        m = a.static_mesh_component.static_mesh
        if not m: continue
        mn = m.get_name()
        if any(k in mn for k in WALLS):
            o, e = a.get_actor_bounds(False)
            top = o.z + e.z
            if e.z * 2 < 100: continue
            t = E.spawn_actor_from_object(cube, V(o.x, o.y, top + 200), a.get_actor_rotation())
            # cube is 100 units; size the block to the wall's local footprint
            ls = a.static_mesh_component.get_local_bounds() if hasattr(a.static_mesh_component, "get_local_bounds") else None
            sc = a.get_actor_scale3d(); bb = m.get_bounding_box()
            t.set_actor_scale3d(V(max((bb.max.x - bb.min.x) * sc.x, 20) / 100.0, max((bb.max.y - bb.min.y) * sc.y, 20) / 100.0, 4.0))
            c = t.static_mesh_component; c.set_material(0, inv); c.set_collision_profile_name("BlockAll"); c.set_cast_shadow(False)
            c.set_editor_property("hidden_in_game", True)
            t.set_actor_label(f"WallTop_{out['tops']}"); t.set_folder_path("Gameplay/WallTops"); out["tops"] += 1
        if any(k in mn for k in WOOD) and mn not in out["wood_meshes"]:
            bs = m.get_editor_property("body_setup")
            bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            EAL.save_loaded_asset(m, False); out["wood_meshes"].append(mn)
    return out

def player_height():
    bp = EAL.load_asset(f"{R}/Core/BP_TUMCharacter"); cdo = unreal.get_default_object(bp.generated_class())
    cap = cdo.get_editor_property("capsule_component")
    return cap.get_editor_property("capsule_half_height") * 2.0
def soldiers():
    target = 186.0  # the first-person eye sits at ~174 cm, so people around must be ~1.86 m to read as the same height
    P = unreal.AnimPoseExtensions; opts = unreal.AnimPoseEvaluationOptions()
    anim = S.A("Right_Hand_Sword_Slash"); pose = P.get_anim_pose_at_time(anim, 0.0, opts)
    W = lambda b: P.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD)
    hand = W("hand_r"); mid = W("middle_01_r").translation; idx = W("index_01_r").translation; pky = W("pinky_01_r").translation
    hp = hand.translation
    blade_w = V(idx.x - pky.x, idx.y - pky.y, idx.z - pky.z); palm_w = V((hp.x + mid.x) / 2, (hp.y + mid.y) / 2, (hp.z + mid.z) / 2)
    blade_l = unreal.MathLibrary.inverse_transform_direction(hand, blade_w); blade_l = blade_l.normal()
    fing_l = unreal.MathLibrary.inverse_transform_direction(hand, V(mid.x - hp.x, mid.y - hp.y, mid.z - hp.z)).normal()
    palm_l = unreal.MathLibrary.inverse_transform_location(hand, palm_w)
    rot = unreal.MathLibrary.make_rot_from_zx(blade_l, fing_l)
    sw = EAL.load_asset(S.SWORD); bb = sw.get_bounding_box(); grip_z = bb.min.z + 0.12 * (bb.max.z - bb.min.z)
    try: off = V(0, 0, grip_z).rotate(rot)
    except Exception: off = unreal.MathLibrary.greater_greater_vector_rotator(V(0, 0, grip_z), rot)
    loc = V(palm_l.x - off.x, palm_l.y - off.y, palm_l.z - off.z)
    out = {"target": round(target), "rot": [round(rot.roll), round(rot.pitch), round(rot.yaw)], "loc": [round(loc.x, 1), round(loc.y, 1), round(loc.z, 1)], "scaled": 0, "swords": 0}
    heights = {}
    for a in E.get_all_level_actors():
        if not isinstance(a, unreal.SkeletalMeshActor): continue
        lab = a.get_actor_label()
        mesh = a.skeletal_mesh_component.get_skeletal_mesh_asset()
        if not mesh or "/War/Soldiers/" not in mesh.get_path_name(): continue
        mp = mesh.get_path_name()
        if mp not in heights:
            b = mesh.get_bounds(); heights[mp] = b.box_extent.z * 2.0
        if not lab.startswith("Cavalry_"):
            s = target / max(heights[mp], 1.0) * random.uniform(0.97, 1.03)
            a.set_actor_scale3d(V(s, s, s)); out["scaled"] += 1
        for ch in a.get_attached_actors():
            if ch.get_actor_label().endswith("_Sword"):
                ch.root_component.set_relative_rotation(rot, False, False); ch.root_component.set_relative_location(loc, False, False); out["swords"] += 1
    out["mesh_heights"] = {k.split("/")[-1]: round(v) for k, v in heights.items()}
    return out

def more_threats():
    random.seed(4545)
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(("KnightFar_", "ArchersFar_")):
            for ch in a.get_attached_actors(): E.destroy_actor(ch)
            E.destroy_actor(a)
    import tum_s335 as M
    obs = M.obstacles()
    kcls = EAL.load_asset(f"{WB}/BP_Knight").generated_class(); made = 0; tries = 0; ks = []
    clashes = [EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Clash_{i}") for i in range(1, 11)]
    swing = EAL.load_asset(f"{R}/Audio/SFX/Sword/SFX_Swing_2")
    tmpl = [a for a in E.get_all_level_actors() if a.get_class().get_name() == "BP_Knight_C"]
    while made < 9 and tries < 6000:
        tries += 1
        x = random.uniform(6300, 9500); y = random.uniform(-3800, 3800)
        if any(M.inside(x, y, b, 150) for b in obs) or any(math.hypot(x - kx, y - ky) < 900 for kx, ky in ks): continue
        ks.append((x, y))
        k = E.spawn_actor_from_class(kcls, V(x, y, 0), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360))); k.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        body = S.soldier(f"KnightFar_{made}_Body", x, y, 2, 180, "Walking", "Art/War/Battle/Knights")
        body.attach_to_actor(k, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        body.root_component.set_relative_rotation(unreal.Rotator(roll=0, pitch=0, yaw=-90), False, False)
        for kk, vv in (("Body", body), ("RunAnim", S.A("RunFast")), ("IdleAnim", S.A("Sword_Parry")), ("WalkAnim", S.A("Walking")), ("HitAnim", S.A("Right_Hand_Sword_Slash")), ("DieAnim", S.A("dying_backwards")), ("ReactAnim", S.A("Face_Punch_Reaction"))):
            k.set_editor_property(kk, vv)
        k.set_editor_property("Clang", random.choice(clashes)); k.set_editor_property("Shout", swing)
        if tmpl:
            for pn in ("Speed", "Sight"): k.set_editor_property(pn, tmpl[0].get_editor_property(pn))
        k.tags = [unreal.Name("Knight")]; k.set_actor_label(f"KnightFar_{made}"); k.set_folder_path("Art/War/Battle/Knights"); made += 1
    return {"knights": made, "archer_groups": 0}

def goal():
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() in ("Goal_Beacon",): E.destroy_actor(a)
    p = f"{R}/Materials/M_SealGlow"
    if not EAL.does_asset_exist(p):
        m = AT.create_asset("M_SealGlow", f"{R}/Materials", unreal.Material, unreal.MaterialFactoryNew())
        m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        c = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -500, 0); c.set_editor_property("constant", unreal.LinearColor(1.0, 0.62, 0.22, 1))
        fr = MEL.create_material_expression(m, unreal.MaterialExpressionFresnel, -700, 200); fr.set_editor_property("exponent", 2.0)
        ad = MEL.create_material_expression(m, unreal.MaterialExpressionAdd, -500, 200); ad.set_editor_property("const_b", 0.6); MEL.connect_material_expressions(fr, "", ad, "A")
        mu = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 0); MEL.connect_material_expressions(c, "", mu, "A"); MEL.connect_material_expressions(ad, "", mu, "B")
        k = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -150, 0); k.set_editor_property("const_b", 14.0); MEL.connect_material_expressions(mu, "", k, "A")
        MEL.connect_material_property(k, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        MEL.recompile_material(m); EAL.save_loaded_asset(m, False)
    mat = EAL.load_asset(p); out = {}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if lab == "Goal_Seal":
            sc = a.get_actor_scale3d(); a.set_actor_scale3d(V(sc.x * 1.4, sc.y * 1.4, sc.z * 1.4))
            for i in range(a.static_mesh_component.get_num_materials()): a.static_mesh_component.set_material(i, mat)
            out["seal"] = str(a.get_actor_location())
        if lab == "Goal_BeaconLight":
            pc = a.point_light_component; pc.set_intensity(9000.0); pc.set_attenuation_radius(1400.0)
            l = a.get_actor_location(); a.set_actor_location(V(l.x, l.y, l.z - 120), False, False)
    return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("horses", horses)
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("walls_and_wood", walls_and_wood); step("soldiers", soldiers); step("more_threats", more_threats); step("goal", goal)
    L.save_current_level()
    return res

def run_soldiers():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField"); step("soldiers", soldiers); L.save_current_level(); return res
