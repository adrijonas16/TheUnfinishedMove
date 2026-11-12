# Dress moving hazards + hanging cloth: crusher = swinging bundle of rusty steel beams on a crane hook, patrol = searchlight, cloth from ceiling
import unreal, importlib, random
import tum_art as A; importlib.reload(A)
import tum_ph as PH; importlib.reload(PH)
V = unreal.Vector
def E(): return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def find(l): return [a for a in E().get_all_level_actors() if a.get_actor_label() == l]
def dress_on(body, sub, size, label, offs=(0, 0, 0), rot=(0, 0, 0), uniform=False):
    o, e = body.get_actor_bounds(False)
    a = A.place(sub, o.x + offs[0], o.y + offs[1], o.z - e.z + offs[2], size=size, uniform=uniform, yaw=rot[1], pitch=rot[0], roll=rot[2], folder="Art/Dress/Movers", label=label)
    a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    a.attach_to_actor(body, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    return a
def run():
    for a in E().get_all_level_actors():
        if str(a.get_folder_path()).startswith("Art/Dress/Movers") or a.get_actor_label().startswith("Cloth_Hang_"): E().destroy_actor(a)
    PH.fetch_and_import(["portable_searchlight"]); A._cache.clear()
    out = []
    for b in find("FocusGate_Crusher_Body"):
        o, e = b.get_actor_bounds(False); out.append(("crusher", [round(2 * e.x), round(2 * e.y), round(2 * e.z)]))
        for i in range(3):
            dress_on(b, "Beam_Metal_Rusty_02_" + "ABC"[i], (2 * e.x, None, None), f"Crusher_Beam_{i}", offs=(0, (i - 1) * e.y * 0.6, e.z * 0.6 + i * 12), uniform=True)
        b.set_actor_hidden_in_game(True)
    for b in find("Diag_Patrol_Body"):
        dress_on(b, "portable_searchlight", (None, None, 90), "Patrol_Searchlight", uniform=True)
        b.set_actor_hidden_in_game(True)
    rnd = random.Random(4)
    for i in range(14):
        x = 600 + i * 640 + rnd.uniform(-150, 150); y = rnd.choice([-1, 1]) * rnd.uniform(250, 1100)
        t = A.place("Tarp_Wrinkled_0" + str(1 + i % 2), x, y, 520, size=(None, None, 360), uniform=True, pitch=90, yaw=rnd.uniform(0, 360), folder="Art/Dress/Cloth", label=f"Cloth_Hang_{i}", base=False)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return out
