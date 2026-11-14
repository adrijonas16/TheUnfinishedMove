# War collision pass: no invisible blockers, small rocks/debris walkable, solid props really solid
# (meshes without simple collision use their real shape), lone fighting soldiers hidden, higher step-up.
import unreal, math, collections
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SMS = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
SOLID = ("Wooden_Beam", "Wooden_Crate", "Wooden_Barrel", "Stakes", "Brick_Walls", "Ruins_Wall", "ChurchRuin", "Plank", "Rope_Coil", "CatapultBase", "Dead_Tree", "Boulder", "Limestone_Slab")
SMALL = ("Scatter_Rock", "Limestone_Rocks", "Rubble", "Beach_Rock", "Debris", "Skull", "Tree_Branch", "Branch_Debris", "boulder_01", "rock_moss")
FIGHT = ("Sword", "Shield", "Parry", "Punch", "Judgment", "Slash")
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level("/Game/TUM/Maps/M_Cut_WarField")
    out = collections.Counter(); fixed_meshes = []
    acts = list(E.get_all_level_actors())
    for a in acts:
        if not isinstance(a, unreal.StaticMeshActor): continue
        c = a.static_mesh_component; m = c.static_mesh
        if not m: continue
        lab = a.get_actor_label(); mn = m.get_name()
        hidden = a.is_hidden_ed() or c.get_editor_property("hidden_in_game") or not c.get_editor_property("visible")
        if hidden and lab not in ("Bound_War_0", "Bound_War_1", "Bound_War_2", "Bound_War_3") and not lab.startswith("Bound"):
            if str(c.get_collision_enabled()) != "CollisionEnabled.NO_COLLISION":
                c.set_collision_profile_name("NoCollision"); a.set_actor_enable_collision(False); out["hidden_off"] += 1
            continue
        o, e = a.get_actor_bounds(False); h = e.z * 2
        if any(k in mn for k in SMALL) and h < 100:
            c.set_collision_profile_name("NoCollision"); out["small_off"] += 1; continue
        if any(k in mn for k in SOLID):
            if mn not in fixed_meshes:
                try: n = SMS.get_simple_collision_count(m)
                except Exception: n = -1
                if n == 0:
                    bs = m.get_editor_property("body_setup")
                    bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
                    EAL.save_loaded_asset(m, False); fixed_meshes.append(mn)
            c.set_collision_profile_name("BlockAll"); a.set_actor_enable_collision(True); out["solid"] += 1
    # lone fighters: a fight-animated soldier with no other fighter within 3 m is hidden
    fighters = []
    for a in acts:
        if isinstance(a, unreal.SkeletalMeshActor) and not a.is_hidden_ed():
            an = a.skeletal_mesh_component.get_editor_property("animation_data").get_editor_property("anim_to_play")
            if an and any(k in an.get_name() for k in FIGHT): fighters.append(a)
    lone = []
    for a in fighters:
        p = a.get_actor_location()
        if not any(b is not a and math.hypot(b.get_actor_location().x - p.x, b.get_actor_location().y - p.y) < 300 for b in fighters):
            lone.append(a)
    for a in lone:
        a.set_actor_hidden_in_game(True)
        for ch in a.get_attached_actors(): ch.set_actor_hidden_in_game(True)
    out["fighters"] = len(fighters); out["lone_hidden"] = len(lone)
    L.save_current_level()
    bp = EAL.load_asset("/Game/TUM/Core/BP_TUMCharacter"); cdo = unreal.get_default_object(bp.generated_class())
    cm = cdo.get_editor_property("character_movement"); cm.set_editor_property("max_step_height", 60.0)
    BEL.compile_blueprint(bp); EAL.save_loaded_asset(bp, False)
    return {"counts": dict(out), "complex_as_simple": fixed_meshes}
