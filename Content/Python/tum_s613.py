# War fixes after playtest: animate copied soldiers behind the start, ground behind the start, camera at eye height.
import unreal, random, traceback
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; R = "/Game/TUM"; CH = "/Game/TUM/Core/BP_TUMCharacter"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]

def war():
    random.seed(7)
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    acts = list(E.get_all_level_actors()); out = {}
    ps = [a for a in acts if isinstance(a, unreal.PlayerStart)]
    sx = ps[0].get_actor_location().x if ps else 0.0; out["start"] = str(ps[0].get_actor_location()) if ps else None
    beh = [a for a in acts if a.get_actor_label().startswith("Behind_")]
    out["behind_by_class"] = {}
    for a in beh:
        k = a.get_class().get_name(); out["behind_by_class"][k] = out["behind_by_class"].get(k, 0) + 1
    # fight animations taken from the existing duel soldiers
    anims = []
    for a in acts:
        if a.get_actor_label().startswith("Duel2_") and isinstance(a, unreal.SkeletalMeshActor):
            d = a.skeletal_mesh_component.get_editor_property("animation_data"); an = d.get_editor_property("anim_to_play")
            if an and an not in anims: anims.append(an)
    out["anims"] = len(anims); fixed = 0
    for a in beh:
        if isinstance(a, unreal.SkeletalMeshActor) and anims:
            c = a.skeletal_mesh_component
            c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            d = unreal.SingleAnimationPlayData(); d.set_editor_property("anim_to_play", random.choice(anims))
            d.set_editor_property("saved_looping", True); d.set_editor_property("saved_playing", True)
            d.set_editor_property("saved_position", random.uniform(0, 1)); d.set_editor_property("saved_play_rate", random.uniform(0.9, 1.1))
            c.set_editor_property("animation_data", d); fixed += 1
    out["animated"] = fixed
    # ground behind the start: copy ground tiles from in front, twice
    tiles = [a for a in acts if a.get_actor_label().startswith(("GT", "Ground", "War_Ground")) and isinstance(a, unreal.StaticMeshActor)]
    xs = [t.get_actor_location().x for t in tiles]
    out["tiles"] = len(tiles); out["tile_minx"] = min(xs) if xs else None
    world = unreal.EditorLevelLibrary.get_editor_world()
    for a in acts:
        if a.get_actor_label().startswith("BehindGround_"): E.destroy_actor(a)
    if xs:
        mn = min(xs); band = [t for t in tiles if mn <= t.get_actor_location().x < mn + 3000]
        n = 0
        for off in (-3000, -6000):
            for d in E.duplicate_actors(band, world, V(off, 0, 0)):
                d.set_actor_label(f"BehindGround_{n}"); d.set_folder_path("Art/War/Behind"); n += 1
        out["ground_copies"] = n
    L.save_current_level(); return out

def camera():
    bp = EAL.load_asset(CH)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); F = unreal.SubobjectDataBlueprintFunctionLibrary
    hs = {str(F.get_variable_name(F.get_data(h))): h for h in sds.k2_gather_subobject_data_for_blueprint(bp)}
    boom = F.get_object(F.get_data(hs["CameraBoom"]))
    old = boom.get_editor_property("relative_location")
    boom.set_editor_property("relative_location", V(0, 0, 78))
    BEL.compile_blueprint(bp); EAL.save_loaded_asset(bp, False); return f"{old} -> z78"

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("war", war); step("camera", camera); return res
