# Replace visible gameplay cubes with real shapes: rubble heaps for steps/stairs, rusty I-beams for the crane, chess set on the real table
import unreal, importlib, random
import tum_art as A; importlib.reload(A)
V = unreal.Vector
def E(): return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def acts(): return {a.get_actor_label(): a for a in E().get_all_level_actors()}
def cover(label, sub, yaw=0.0, extra=1.15, pitch=0.0, swap=False):
    a = acts().get(label)
    if not a: return None
    o, e = a.get_actor_bounds(False)
    sx, sy, sz = 2 * e.x * extra, 2 * e.y * extra, 2 * e.z
    if swap: sx, sz = sz, sx
    d = A.place(sub, o.x, o.y, o.z - e.z if not swap else o.z, size=(sx, sy, sz), uniform=False, yaw=yaw, pitch=pitch, folder="Art/Dress/Cover", label=f"Cover_{label}", base=not swap)
    a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True)
    return d.get_actor_label()
def run():
    for a in E().get_all_level_actors():
        if str(a.get_folder_path()).startswith("Art/Dress/Cover") or a.get_actor_label().startswith("ChessSet_"): E().destroy_actor(a)
    A._cache.clear(); rnd = random.Random(7); out = []
    for l, m in (("Entry_BrokenStair", "Rubble_Pile_Concrete_M_01"), ("DragonStep_0", "Rubble_Pile_Concrete_M_02"), ("DragonStep_1", "Rubble_Pile_Concrete_M_01"),
                 ("DragonStep_2", "Rubble_Pile_Concrete_M_02"), ("Catwalk_Stairs", "Rubble_Pile_Concrete_M_01"), ("Exit_ExposePiece_Hatch", "Rubble_Pile_Concrete_M_02")):
        out.append(cover(l, m, yaw=rnd.uniform(0, 360) if l != "Catwalk_Stairs" else 0.0))
    out.append(cover("Crane_Mast", "Beam_Metal_Rusty_02_A", pitch=90.0, extra=1.0, swap=True))
    out.append(cover("Crane_Arm", "Beam_Metal_Rusty_02_B", extra=1.0))
    # chess: graybox table/board/chairs hidden (real table + metal chairs already there), Poly Haven chess set on the board
    for l in ("Chess_Table", "Chess_Board", "Chess_ChairA", "Chess_ChairB"):
        a = acts().get(l)
        if a: a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True)
    t = [a for a in E().get_all_level_actors() if a.get_actor_label().startswith("Art_SM_Ind_Ware_Furn_Table_Wood_Worn_01_A")]
    if t:
        o, e = t[0].get_actor_bounds(False); top = o.z + e.z
        import tum_s107 as S; importlib.reload(S)
        for i, x in enumerate(S.ph("chess_set", o.x, o.y, top, yaw=90.0, scale=1.0, label="ChessSet", folder="Art/Factory/Chess")): pass
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return out
