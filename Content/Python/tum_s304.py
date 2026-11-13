# Title screen (in the room, before control is given) + real music on every map
import unreal, importlib, traceback, math
import tum_s258 as T; importlib.reload(T)
EAL = unreal.EditorAssetLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
V = unreal.Vector; MUS = "/Game/TUM/Audio/Music"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
def find(label):
    for a in E.get_all_level_actors():
        if a.get_actor_label() == label: return a
def snd(name, loop=True):
    s = EAL.load_asset(f"{MUS}/{name}"); s.set_editor_property("looping", loop); EAL.save_loaded_asset(s, False); return s
def music_actor(label, sound, tag, auto, vol=0.6):
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() == label: E.destroy_actor(a)
    a = E.spawn_actor_from_class(unreal.AmbientSound, V(0, 0, 0), unreal.Rotator())
    c = a.get_component_by_class(unreal.AudioComponent)
    c.set_editor_property("sound", sound); c.set_editor_property("auto_activate", auto); c.set_editor_property("volume_multiplier", vol)
    c.set_editor_property("allow_spatialization", False); c.set_editor_property("is_ui_sound", False)
    a.set_actor_label(label); a.tags = [tag]; a.set_folder_path("Audio"); return a
def text(name, msg, loc, yaw, size, color, tag):
    t = E.spawn_actor_from_class(unreal.TextRenderActor, V(*loc), unreal.Rotator(roll=0, pitch=0, yaw=yaw))
    tc = t.text_render; tc.set_text(unreal.Text(msg)); tc.set_world_size(size); tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    tc.set_text_render_color(unreal.Color(r=color[0], g=color[1], b=color[2], a=255)); tc.set_cast_shadow(False)
    t.tags = [tag]; t.set_actor_label(name); t.set_folder_path("UI/Title"); return t

def room():
    L.load_level("/Game/TUM/Maps/M_RealRoom")
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(("Title_", "Cine_Title")): E.destroy_actor(a)
    cam_loc = V(-250, -200, 175); look = V(0, 250, 120)
    c = E.spawn_actor_from_class(unreal.CineCameraActor, cam_loc, unreal.Rotator())
    d = look - cam_loc
    c.set_actor_rotation(unreal.Rotator(roll=0, pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x))), False)
    cc = c.get_cine_camera_component(); cc.set_editor_property("current_focal_length", 24.0)
    fs = cc.get_editor_property("focus_settings"); fs.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE); cc.set_editor_property("focus_settings", fs)
    c.set_actor_label("Cine_Title"); c.tags = ["Cine_Title"]; c.set_folder_path("Cinematic")
    # title floats in the dark room, facing the camera
    fwd = d * (1.0 / d.length()); right = V(fwd.y, -fwd.x, 0)
    yaw = math.degrees(math.atan2(-fwd.y, -fwd.x))
    base = cam_loc + fwd * 220
    text("Title_Main", "THE UNFINISHED MOVE", (base.x, base.y, base.z + 18), yaw, 14.0, (240, 236, 228), "TitleUI")
    text("Title_Sub", "a memory you never finished", (base.x, base.y, base.z + 4), yaw, 4.2, (255, 205, 150), "TitleUI")
    text("Title_Start", "Press  E  to begin", (base.x, base.y, base.z - 26), yaw, 4.0, (210, 220, 235), "TitleUI")
    text("Title_Credit", "Epic AI MegaJam 2026", (base.x, base.y, base.z - 36), yaw, 2.4, (150, 150, 160), "TitleUI")
    music_actor("Title_Music", snd("MUS_alexander_nakarada_emotional_ballad"), "TitleMusic", False, 0.55)
    im = find("Intro_Music")
    if im:
        ac = im.get_component_by_class(unreal.AudioComponent); ac.set_editor_property("sound", snd("MUS_scott_buckley_what_we_dont_say")); ac.set_editor_property("volume_multiplier", 0.8)
    L.save_current_level(); return "ok"
def maps():
    out = {}
    for mp, track, vol in (("M_FactoryHub", "MUS_scott_buckley_undertow", 0.35), ("M_Cut_Dragon", "MUS_scott_buckley_a_kind_of_hope", 0.6),
                           ("M_Cut_WarField", "MUS_alexander_nakarada_downfall", 0.5), ("M_Cut_Cliff", "MUS_punch_deck_grey_sky", 0.5)):
        L.load_level(f"/Game/TUM/Maps/{mp}"); music_actor("Level_Music", snd(track), "LevelMusic", True, vol); L.save_current_level(); out[mp] = track
    return out
def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("director", T.director)
    return res
