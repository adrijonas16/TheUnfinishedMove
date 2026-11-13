# Procedural AnimSequences on the UE5 mannequin skeleton (keyframed bone-space rotations)
import unreal, math
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
SKEL = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
DEST = "/Game/TUM/Anims"
FPS = 30
def _q(rx, ry, rz):
    return unreal.Rotator(roll=rx, pitch=ry, yaw=rz).quaternion()
def make(name, keys, length, loop_smooth=False):
    """keys: list of (time_s, {bone: (roll, pitch, yaw) degrees in bone space}, {bone: (dx,dy,dz) local translation offsets}).
    Bones absent from a key keep the reference pose. Linear interpolation between keys with smoothstep easing."""
    skel = EAL.load_asset(SKEL)
    p = f"{DEST}/{name}"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    f = unreal.AnimSequenceFactory(); f.set_editor_property("target_skeleton", skel)
    seq = AT.create_asset(name, DEST, unreal.AnimSequence, f)
    ref = unreal.AnimPoseExtensions.get_reference_pose(skel)
    bones = sorted(set(b for k in keys for b in list(k[1].keys()) + list(k[2].keys())))
    n = int(round(length * FPS)) + 1
    ctrl = seq.controller
    ctrl.open_bracket(unreal.Text("tum procedural"), False)
    ctrl.set_frame_rate(unreal.FrameRate(FPS, 1), False)
    ctrl.set_number_of_frames(unreal.FrameNumber(n - 1), False)
    def sample(t, bone):
        ks = keys
        if t <= ks[0][0]: a = b = ks[0]; u = 0.0
        elif t >= ks[-1][0]: a = b = ks[-1]; u = 0.0
        else:
            for i in range(len(ks) - 1):
                if ks[i][0] <= t <= ks[i + 1][0]: a, b = ks[i], ks[i + 1]; break
            u = (t - a[0]) / max(b[0] - a[0], 1e-4); u = u * u * (3 - 2 * u)
        ra = a[1].get(bone, (0, 0, 0)); rb = b[1].get(bone, (0, 0, 0))
        ta = a[2].get(bone, (0, 0, 0)); tb = b[2].get(bone, (0, 0, 0))
        r = tuple(ra[j] + (rb[j] - ra[j]) * u for j in range(3)); tr = tuple(ta[j] + (tb[j] - ta[j]) * u for j in range(3))
        return r, tr
    for bone in bones:
        rt = unreal.AnimPoseExtensions.get_bone_pose(ref, bone, unreal.AnimPoseSpaces.LOCAL)
        pos, rot, scl = [], [], []
        for i in range(n):
            r, tr = sample(i / FPS, bone)
            q = rt.rotation * _q(*r)
            pos.append(unreal.Vector(rt.translation.x + tr[0], rt.translation.y + tr[1], rt.translation.z + tr[2])); rot.append(q); scl.append(rt.scale3d)
        try: ctrl.add_bone_curve(bone, False)
        except Exception:
            try: ctrl.add_bone_track(bone, False)
            except Exception: pass
        ctrl.set_bone_track_keys(bone, pos, rot, scl, False)
    ctrl.close_bracket(False)
    EAL.save_loaded_asset(seq, False)
    return seq
