# Factory cleanup: no crates/containers/cardboard rows, open chess nave (table only), sky dome
import unreal
EAL = unreal.EditorAssetLibrary; V = unreal.Vector
def E(): return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def hide(a):
    a.set_actor_hidden_in_game(True); a.set_actor_enable_collision(False); a.set_is_temporarily_hidden_in_editor(True)
def run():
    out = {"deleted": 0, "hidden": []}
    for a in E().get_all_level_actors():
        l = a.get_actor_label(); f = str(a.get_folder_path())
        bad = any(k in l for k in ("Container", "Pallet", "Cardboard", "Crate", "Storage_Sheet", "Oil_Plastic"))
        if f.startswith("Art") and bad: E().destroy_actor(a); out["deleted"] += 1; continue
        if f.startswith("Chess/Cell") or l in ("Block_Crate",) or f.startswith("Chess/Pads"):
            hide(a); out["hidden"].append(l)
        if l.startswith("Loom_") and f.startswith("Graybox"):
            a.set_actor_hidden_in_game(True)   # collision stays; Meshy loom dresses it
    # night sky dome like the bedroom (city HDRI) so roof gaps / windows show sky
    if not [a for a in E().get_all_level_actors() if a.get_actor_label() == "City_Dome"]:
        d = E().spawn_actor_from_object(EAL.load_asset("/Engine/BasicShapes/Sphere"), V(4000, 0, -20000), unreal.Rotator(0, 0, 0))
        d.set_actor_scale3d(V(3000, 3000, 3000)); c = d.static_mesh_component; c.set_material(0, EAL.load_asset("/Game/TUM/Materials/Surfaces/MI_CityBackdrop"))
        c.set_collision_profile_name("NoCollision"); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); c.set_cast_shadow(False)
        d.set_actor_label("City_Dome"); d.set_folder_path("Art/City"); d.tags = [unreal.Name("ArtPass")]
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return out
