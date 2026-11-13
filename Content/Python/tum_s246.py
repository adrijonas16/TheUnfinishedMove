# Factory: last graybox pieces -> real models (catwalk planks/beams, anchors as real objects, faceless night-guard patrol)
import unreal, math, random, traceback
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; KW = unreal.AttachmentRule.KEEP_WORLD; MOV = unreal.ComponentMobility.MOVABLE
DC = "/Game/DerelictCorridor/Assets/Fab/Megascans/3D"; MS = "/Game/MS/3D"
INV = "/Game/TUM/Materials/Surfaces/M_Invisible"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1200:]
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a
def first(folder):
    ps = [p for p in EAL.list_assets(folder, False, False) if "/SM_" in p.split(".")[0].split("/")[-1] or p.split("/")[-1].startswith("SM_")]
    if not ps: raise RuntimeError("no SM in " + folder)
    return EAL.load_asset(ps[0])
def fit_into(mesh, center, size, yaw=0.0, pitch=0.0, roll=0.0, name="Art", folder="Art/Factory/GrayboxSkins"):
    b = mesh.get_bounding_box(); ext = b.max - b.min
    a = E.spawn_actor_from_object(mesh, V(0, 0, 0), unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw))
    # measure rotated extents at scale 1
    o, e = a.get_actor_bounds(False)
    a.set_actor_scale3d(V(1, 1, 1))
    sx, sy, sz = size[0] / max(2 * e.x, 1), size[1] / max(2 * e.y, 1), size[2] / max(2 * e.z, 1)
    # rotated: approximate by mapping world extents back to local scale (works for 0/90 rotations)
    if abs(math.sin(math.radians(yaw))) > 0.5: sx, sy = sy, sx
    if abs(math.sin(math.radians(pitch))) > 0.5: sx, sz = sz, sx
    if abs(math.sin(math.radians(roll))) > 0.5: sy, sz = sz, sy
    a.set_actor_scale3d(V(sx, sy, sz))
    o, e = a.get_actor_bounds(False)
    l = a.get_actor_location(); a.set_actor_location(V(l.x + center[0] - o.x, l.y + center[1] - o.y, l.z + center[2] - o.z), False, False)
    a.set_actor_enable_collision(False); a.set_actor_label(name); a.set_folder_path(folder)
    return a
def invisible(a):
    c = a.static_mesh_component; m = EAL.load_asset(INV)
    for i in range(c.get_num_materials()): c.set_material(i, m)
def bounds(a):
    o, e = a.get_actor_bounds(False); return (o.x, o.y, o.z), (2 * e.x, 2 * e.y, 2 * e.z)
def attach(child, parent):
    child.root_component.set_mobility(MOV); child.attach_to_actor(parent, "", KW, KW, KW, False)

def run_all():
    for a in list(E.get_all_level_actors()):
        if str(a.get_folder_path()).startswith("Art/Factory/GrayboxSkins"): E.destroy_actor(a)
    plank = first(f"{DC}/Ind_Con_Supplies_Plank_Wood_Long_01"); plank2 = first(f"{DC}/Ind_Con_Supplies_Plank_Wood_Long_02")
    beam = first(f"{DC}/Ind_Con_Supplies_Beam_Metal_Rusty_02")
    out = {}
    random.seed(21)
    # walkable catwalks / ledge: invisible collision + plank deck on two rusty beams
    for n in ("Entry_HighCatwalk", "Catwalk_Raised", "Exit_BlockExit_BrokenCatwalk", "Cliff_Ledge"):
        a = find(n)
        if not a: continue
        (cx, cy, cz), (sx, sy, sz) = bounds(a); invisible(a)
        along_x = sx >= sy
        L_, W_ = (sx, sy) if along_x else (sy, sx)
        k = max(2, int(W_ / 45))
        for i in range(k):
            off = -W_ / 2 + (i + 0.5) * W_ / k
            c = (cx, cy + off, cz + sz / 2 - 4) if along_x else (cx + off, cy, cz + sz / 2 - 4)
            p = fit_into(random.choice((plank, plank2)), c, (L_ * random.uniform(0.94, 1.0), W_ / k * 0.92, 8) if along_x else (W_ / k * 0.92, L_ * random.uniform(0.94, 1.0), 8),
                         yaw=0 if along_x else 90, name=f"Skin_{n}_P{i}")
            if a.get_attach_parent_actor() or a.root_component.mobility == MOV: attach(p, a)
        for side in (-1, 1):
            off = side * (W_ / 2 - 8)
            c = (cx, cy + off, cz - 10) if along_x else (cx + off, cy, cz - 10)
            fit_into(beam, c, (L_, 16, 22) if along_x else (16, L_, 22), name=f"Skin_{n}_B{side}")
        out[n] = k
    # anchors: same silhouettes, real objects
    lamp = first(f"{DC}/Ind_Ware_Light_Ceiling_Metal_Hanging_01"); drain = first(f"{DC}/Ind_Junk_Cover_Drain_Metal_Rusty_01")
    door = first(f"{MS}/Old_Wooden_Door_uflvddofa"); pole = first(f"{MS}/Old_Wooden_Pole_ueqfdi0ga"); tarp = first(f"{DC}/Ind_AbaFact_Tarp_Wrinkled_01")
    for n, mesh, rot in (("Anchor_Dragon_Lamp", drain, (0, 0, 90)), ("Anchor_Dragon_RoundWindow", drain, (0, 0, 90)), ("Anchor_Dragon_Spot", drain, (0, 0, 0)),
                          ("Anchor_War_Spot", drain, (0, 0, 0)), ("Anchor_War_Window", door, (90, 0, 0)), ("Anchor_War_Banner", tarp, (90, 0, 90)),
                          ("Anchor_Cliff_Slit", pole, (0, 0, 0))):
        a = find(n)
        if not a: continue
        (cx, cy, cz), size = bounds(a)
        yaw, pitch, roll = rot
        try:
            s = fit_into(mesh, (cx, cy, cz), size, yaw=yaw, pitch=pitch, roll=roll, name=f"Skin_{n}")
            invisible(a); out[n] = "skinned"
        except Exception as ex: out[n] = repr(ex)
    # the lamp anchor also gets a real hanging lamp above it
    a = find("Anchor_Dragon_Lamp")
    if a:
        (cx, cy, cz), _ = bounds(a)
        fit_into(lamp, (cx, cy, cz + 90), (90, 90, 120), name="Skin_Lamp_Hang")
    # shuttles (movers): rusty beams riding the mover
    for n in ("BigLoom_Shuttle", "Expose_Shuttle_Body"):
        a = find(n)
        if not a: continue
        (cx, cy, cz), (sx, sy, sz) = bounds(a); invisible(a)
        p = fit_into(beam, (cx, cy, cz), (sx, sy, sz * 0.6), name=f"Skin_{n}")
        attach(p, a); out[n] = "skinned"
    # patrol body: a faceless night guard walking with the searchlight
    a = find("PatrolLight_Body")
    if a:
        invisible(a); (cx, cy, cz), (sx, sy, sz) = bounds(a)
        g = E.spawn_actor_from_class(unreal.SkeletalMeshActor, V(cx, cy, cz - sz / 2), unreal.Rotator(roll=0, pitch=0, yaw=-90))
        c = g.skeletal_mesh_component; c.set_mobility(MOV)
        m = EAL.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
        try: c.set_skeletal_mesh_asset(m)
        except Exception: c.set_editor_property("skeletal_mesh_asset", m)
        c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        d = unreal.SingleAnimationPlayData(); d.set_editor_property("anim_to_play", EAL.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd"))
        d.set_editor_property("saved_looping", True); d.set_editor_property("saved_playing", True); c.set_editor_property("animation_data", d)
        c.set_collision_profile_name("NoCollision"); g.set_actor_enable_collision(False)
        g.set_actor_label("Skin_PatrolGuard"); g.set_folder_path("Art/Factory/GrayboxSkins")
        g.attach_to_actor(a, "", KW, KW, KW, False); out["guard"] = "ok"
        pm = a.get_attach_parent_actor() or find("PatrolLight")
        if pm:
            try: pm.set_editor_property("bFaceMotion", True); out["face"] = pm.get_actor_label()
            except Exception as ex: out["face"] = repr(ex)
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_FactoryHub")
    step("factory", run_all)
    return res
