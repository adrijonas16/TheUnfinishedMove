# Abandoned = disorder: looms (and their cover blocks) shifted, turned, tilted, a couple dragged out of line; hanging lights/chains jittered
import unreal, random
V = unreal.Vector
def E(): return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def run(seed=11):
    rnd = random.Random(seed); acts = {a.get_actor_label(): a for a in E().get_all_level_actors()}
    machines = sorted([a for a in acts.values() if a.get_actor_label().startswith("LoomMachine_")], key=lambda a: a.get_actor_label())
    blocks = sorted([a for l, a in acts.items() if (l.startswith("Loom_N") or l.startswith("Loom_S")) and str(a.get_folder_path()).startswith("Graybox")], key=lambda a: a.get_actor_label())
    out = []
    for i, (m, b) in enumerate(zip(machines, blocks)):
        dx = rnd.uniform(-260, 260); dy = rnd.uniform(-160, 160); dyaw = rnd.choice([rnd.uniform(-35, 35), rnd.uniform(60, 120), rnd.uniform(-20, 20)])
        if i in (2, 7): dyaw = rnd.uniform(70, 110); dy += rnd.choice([-1, 1]) * 220   # dragged out of the line
        bp = b.get_actor_location(); b.set_actor_location(V(bp.x + dx, bp.y + dy, bp.z), False, False)
        b.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=b.get_actor_rotation().yaw + dyaw), False)
        mp = m.get_actor_location(); r = m.get_actor_rotation()
        m.set_actor_location(V(mp.x + dx, mp.y + dy, mp.z - rnd.uniform(0, 6)), False, False)
        m.set_actor_rotation(unreal.Rotator(roll=rnd.uniform(-4, 4), pitch=rnd.uniform(-2.5, 2.5), yaw=r.yaw + dyaw), False)
        s = rnd.uniform(0.85, 1.15); sc = m.get_actor_scale3d(); m.set_actor_scale3d(V(sc.x * s, sc.y * s, sc.z * rnd.uniform(0.9, 1.25)))
        out.append((m.get_actor_label(), round(dx), round(dy), round(dyaw)))
    for a in E().get_all_level_actors():
        f = str(a.get_folder_path())
        if f.startswith("Art/Factory/Lights") or f.startswith("Art/Factory/Chains") or f.startswith("Art/Dress/Cloth"):
            p = a.get_actor_location(); a.set_actor_location(V(p.x + rnd.uniform(-220, 220), p.y + rnd.uniform(-180, 180), p.z + rnd.uniform(-60, 40)), False, False)
            r = a.get_actor_rotation(); a.set_actor_rotation(unreal.Rotator(roll=r.roll + rnd.uniform(-6, 6), pitch=r.pitch + rnd.uniform(-4, 4), yaw=r.yaw + rnd.uniform(-40, 40)), False)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return out
