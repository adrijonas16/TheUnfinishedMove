# Real Room: always start the player at the room PlayerStart (tag RoomStart) unless the game has ended
import unreal, importlib
import tum_s38 as S; importlib.reload(S)
import tum_graph as TG; importlib.reload(TG)
def run():
    E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.PlayerStart): a.tags = [unreal.Name("RoomStart")]
        if a.get_actor_label() == "City_Dome": a.set_is_temporarily_hidden_in_editor(False)
    code = f"""
(event EventBeginPlay
  (for s (Actor|GetAllActorswithTag :Tag "RoomStart")
    (Transformation|SetActorLocation :self (Game|GetPlayerCharacter 0) :NewLocation (Transformation|GetActorLocation :self s) :bTeleport true)
    (Transformation|SetActorRotation :self (Game|GetPlayerCharacter 0) :NewRotation (Transformation|GetActorRotation :self s) :bTeleportPhysics true))
  (Utilities|FlowControl|Delay 0.1)
  (bind gi {S.GP}
    (:then
      (bind ended (Class|BPGameProgress|GetGameEnded :self gi))
      {S.show('"Ending"', 'a', '(not ended)')}
      {S.show('"Intro"', 'b', 'ended')}
      (for c (Actor|GetAllActorswithTag :Tag "CutAnchor_Factory") (Actor|Tick|SetActorTickEnabled :self c :bEnabled (not ended))))
    (:CastFailed)))
"""
    r = TG.run(S.RR, code, clear=True)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    return r
