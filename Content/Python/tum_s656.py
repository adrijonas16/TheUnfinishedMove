# Reliable collision: generated collision on these (Nanite/Megascans) meshes stays empty, so each solid prop gets an invisible
# box blocker fitted to its own rotated bounds (shrunk a little for round rocks). Boxes always collide, for you and for horses.
import unreal
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector
KEYS = {"Wooden_Crate": 0.95, "Wooden_Barrel": 0.85, "Wooden_Beam": 0.95, "Plank": 0.95, "Stakes": 0.8, "Old_Wooden_Pole": 0.9,
        "Brick_Walls": 0.97, "Ruins_Wall": 0.97, "ChurchRuin": 0.97, "Beach_Boulder": 0.8, "Nordic_Beach_Boulder": 0.8,
        "Limestone_Slab": 0.9, "CatapultBase": 0.9, "Rope_Coil": 0.85}
for a in list(E.get_all_level_actors()):
    if a.get_actor_label().startswith("Blocker_"): E.destroy_actor(a)
cube = EAL.load_asset("/Engine/BasicShapes/Cube"); inv = EAL.load_asset("/Game/TUM/Materials/Surfaces/M_Invisible")
n = 0; kinds = {}
for a in list(E.get_all_level_actors()):
    if not isinstance(a, unreal.StaticMeshActor) or a.is_hidden_ed(): continue
    m = a.static_mesh_component.static_mesh
    if not m: continue
    k = next((k for k in KEYS if k in m.get_name()), None)
    if not k: continue
    bb = m.get_bounding_box(); sc = a.get_actor_scale3d(); f = KEYS[k]
    cx, cy, cz = (bb.min.x + bb.max.x) / 2, (bb.min.y + bb.max.y) / 2, (bb.min.z + bb.max.z) / 2
    sx, sy, sz = (bb.max.x - bb.min.x) * abs(sc.x) * f, (bb.max.y - bb.min.y) * abs(sc.y) * f, (bb.max.z - bb.min.z) * abs(sc.z)
    if min(sx, sy) < 8 or sz < 25: continue
    rot = a.get_actor_rotation()
    center = a.get_actor_transform().transform_location(V(cx, cy, cz))
    b = E.spawn_actor_from_object(cube, center, rot)
    b.set_actor_scale3d(V(sx / 100.0, sy / 100.0, sz / 100.0))
    c = b.static_mesh_component; c.set_material(0, inv); c.set_collision_profile_name("BlockAll"); c.set_cast_shadow(False)
    c.set_editor_property("hidden_in_game", True)
    b.set_actor_label(f"Blocker_{n}"); b.set_folder_path("Gameplay/Blockers"); n += 1; kinds[k] = kinds.get(k, 0) + 1
L.save_current_level(); RESULT = {"blockers": n, "kinds": kinds}
