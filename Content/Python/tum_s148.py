# Intro cinematic setup: factory spawn inside, earbuds music, three cine cameras in the bedroom
import unreal
EAL = unreal.EditorAssetLibrary; V = unreal.Vector; AT = unreal.AssetToolsHelpers.get_asset_tools()
def E(): return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = lambda: unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
def look(a, b): return unreal.MathLibrary.find_look_at_rotation(V(*a), V(*b))
def factory_spawn():
    LES().load_level("/Game/TUM/Maps/M_FactoryHub")
    for a in E().get_all_level_actors():
        if isinstance(a, unreal.PlayerStart): a.set_actor_location(V(700, 0, 110), False, False); a.set_actor_rotation(unreal.Rotator(roll=0, pitch=0, yaw=0), False)
    LES().save_current_level()
def music():
    t = unreal.AssetImportTask(); t.filename = r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\audio\MUS_Earbuds.wav"; t.destination_path = "/Game/TUM/Audio/Music"
    t.automated = True; t.replace_existing = True; t.save = True; AT.import_asset_tasks([t]); return EAL.load_asset("/Game/TUM/Audio/Music/MUS_Earbuds")
def room(snd):
    LES().load_level("/Game/TUM/Maps/M_RealRoom")
    for a in E().get_all_level_actors():
        if a.get_actor_label() in ("Intro_Music", "Cine_1", "Cine_2", "Cine_3", "Cine_Key"): E().destroy_actor(a)
    m = E().spawn_actor_from_class(unreal.AmbientSound, V(0, 150, 120), unreal.Rotator(0, 0, 0))
    ac = m.get_component_by_class(unreal.AudioComponent); ac.set_editor_property("sound", snd); ac.set_editor_property("auto_activate", False)
    ac.set_editor_property("allow_spatialization", False)
    m.set_actor_label("Intro_Music"); m.set_folder_path("Room/Cine"); m.tags = [unreal.Name("IntroMusic")]
    shots = {"Cine_1": ((-105, 125, 118), (-35, 182, 80), 35.0), "Cine_2": ((-250, 40, 150), (0, 280, 125), 50.0), "Cine_3": ((0, 520, 175), (0, 3000, 300), 30.0)}
    for n, (p, tgt, fov) in shots.items():
        c = E().spawn_actor_from_class(unreal.CineCameraActor, V(*p), look(p, tgt))
        cc = c.get_cine_camera_component(); cc.set_editor_property("current_focal_length", 35.0 * 0 + (36.0 / (2 * __import__("math").tan(__import__("math").radians(fov / 2)))))
        fs = cc.get_editor_property("focus_settings"); fs.focus_method = unreal.CameraFocusMethod.DISABLE; cc.set_editor_property("focus_settings", fs)
        c.set_actor_label(n); c.set_folder_path("Room/Cine"); c.tags = [unreal.Name(n)]
    k = E().spawn_actor_from_class(unreal.SpotLight, V(-60, 120, 160), look((-60, 120, 160), (-35, 182, 77)))
    kc = k.get_component_by_class(unreal.LightComponent); kc.set_intensity(400.0); kc.set_light_color(unreal.LinearColor(1.0, 0.72, 0.45, 1)); kc.set_editor_property("attenuation_radius", 300.0)
    k.set_actor_label("Cine_Key"); k.set_folder_path("Room/Cine")
    for a in E().get_all_level_actors():
        if a.get_actor_label() == "Earbuds": a.tags = list(a.tags) + [unreal.Name("Earbuds")]
        if a.get_actor_label() == "Trigger_Headphones": a.set_editor_property("bCine", True)
    LES().save_current_level()
