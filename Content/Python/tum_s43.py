import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); EAL = unreal.EditorAssetLibrary
M = lambda n: EAL.load_asset(f"/Game/TUM/Materials/Surfaces/MI_{n}")
RULES = {
 "M_FactoryHub": [("Floor", "Concrete034"), ("Roof", "Concrete044A"), ("Wall", "Concrete044A"), ("Cell_", "Concrete044A"), ("Loom", "CorrugatedSteel005"), ("Catwalk", "CorrugatedSteel005"),
                  ("Crane", "CorrugatedSteel005"), ("DragonStep", "CorrugatedSteel005"), ("Ramp", "CorrugatedSteel005"), ("Ledge", "CorrugatedSteel005"), ("Entry_", "CorrugatedSteel005"),
                  ("Table", "Asphalt031"), ("Block_", "CorrugatedSteel005")],
 "M_Cut_WarField": [("Mud_", "Ground080"), ("Floor", "Grass004"), ("Start_Floor", "Grass004"), ("End_Floor", "Ground037"), ("LaneWall", "Rock035"), ("Cover_Wall", "Rock035"),
                    ("Wall_", "Rock030"), ("Wagon", "Ground037"), ("Shrine_P", "Rock030"), ("Shrine_L", "Rock030")],
 "M_Cut_Cliff": [("Ledge", "Rock030"), ("CliffWall", "Rock035"), ("Arch_", "Rock030")],
 "M_Cut_Dragon": [("StormWall", "Rock035")],
 "M_RealRoom": [("Room_Wall", "PaintedPlaster017"), ("Room_Ceiling", "PaintedPlaster017"), ("Room_Floor", "Concrete044A"), ("Desk", "Asphalt031"), ("Bed", "PaintedPlaster017")],
}
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    out = {}
    for mp, rules in RULES.items():
        LES.load_level(f"/Game/TUM/Maps/{mp}"); n = 0
        for a in EAS.get_all_level_actors():
            if not isinstance(a, unreal.StaticMeshActor): continue
            lab = a.get_actor_label()
            for key, mat in rules:
                if key in lab and "_Body" not in lab:
                    a.static_mesh_component.set_material(0, M(mat)); n += 1; break
        LES.save_current_level(); out[mp] = n
    LES.load_level("/Game/TUM/Maps/M_FactoryHub"); return out
