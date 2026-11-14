# War at night: moonlight, dark sky, torches with fire + warm light, rain around the player (War only).
import unreal, importlib, traceback, random, math
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT, _BlueprintCache
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; CH = f"{R}/Core/BP_TUMCharacter"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1800:]
RAIN = r"""
float c = floor(UV.x * 220.0);
float h = frac(sin(c * 12.9898) * 43758.5453);
float y = frac(UV.y * 5.0 + Time * (1.6 + h * 0.8) + h * 10.0);
float streak = smoothstep(0.0, 0.015, y) * (1.0 - smoothstep(0.015, 0.09, y));
float thin = 1.0 - smoothstep(0.0, 0.3, abs(frac(UV.x * 220.0) - 0.5));
return streak * thin * 0.45 * step(0.35, h);
"""
def rain_material():
    p = f"{R}/Materials/Surfaces/M_Rain"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_Rain", f"{R}/Materials/Surfaces", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT); m.set_editor_property("two_sided", True)
    cu = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -300, 0)
    cu.set_editor_property("code", RAIN); cu.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    ins = []
    for n in ("UV", "Time"):
        ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    cu.set_editor_property("inputs", ins)
    uv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -700, -100)
    tm = MEL.create_material_expression(m, unreal.MaterialExpressionTime, -700, 50)
    MEL.connect_material_expressions(uv, "", cu, "UV"); MEL.connect_material_expressions(tm, "", cu, "Time")
    colr = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -300, -200); colr.set_editor_property("constant", unreal.LinearColor(0.55, 0.62, 0.75, 1.0))
    MEL.connect_material_property(colr, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(cu, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); return p

def rain_component():
    bp = EAL.load_asset(CH)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); F = unreal.SubobjectDataBlueprintFunctionLibrary
    hs = {str(F.get_variable_name(F.get_data(h))): h for h in sds.k2_gather_subobject_data_for_blueprint(bp)}
    if "Rain" not in hs:
        p = unreal.AddNewSubobjectParams(parent_handle=hs["CapsuleComponent"], new_class=unreal.StaticMeshComponent, blueprint_context=bp)
        nh, fail = sds.add_new_subobject(p); sds.rename_subobject(nh, unreal.Text("Rain")); hs["Rain"] = nh
    comp = F.get_object(F.get_data(hs["Rain"]))
    comp.set_editor_property("static_mesh", EAL.load_asset("/Engine/BasicShapes/Cylinder"))
    comp.set_material(0, EAL.load_asset(f"{R}/Materials/Surfaces/M_Rain"))
    comp.set_editor_property("relative_scale3d", V(9, 9, 14)); comp.set_editor_property("relative_location", V(0, 0, 150))
    comp.set_collision_profile_name("NoCollision"); comp.set_editor_property("cast_shadow", False); comp.set_editor_property("visible", False)
    BEL.compile_blueprint(bp); EAL.save_loaded_asset(bp, False)
    # BeginPlay: sword into view + rain only where a RainOn marker exists
    import tum_s590 as FP; importlib.reload(FP)
    b = EAL.load_asset(CH); _BlueprintCache.invalidate(b); g = unreal.BlueprintEditorLibrary.find_event_graph(b)
    for n in list(BT.find_nodes(g)):
        t = BT._get_node_info(n).type_id
        if t in ("AddEvent|EventBeginPlay", "Transformation|AttachComponentToComponent", "Transformation|SetRelativeRotation", "Transformation|SetRelativeLocation"): BT.delete_node(n)
    _BlueprintCache.invalidate(b)
    sl, sr = FP.SWORD_LOC, FP.SWORD_ROT
    code = f"""
(event EventBeginPlay
  (Transformation|AttachComponentToComponent :self (Variables|Default|GetSword) :Parent (Variables|Camera|GetFollowCamera) :SocketName "None" :LocationRule "SnapToTarget" :RotationRule "SnapToTarget" :ScaleRule "KeepWorld" :bWeldSimulatedBodies false)
  (Transformation|SetRelativeRotation :self (Variables|Default|GetSword) :NewRotation (Math|Rotator|MakeRotator :Roll {sr[0]} :Pitch {sr[1]} :Yaw {sr[2]}))
  (Transformation|SetRelativeLocation :self (Variables|Default|GetSword) :NewLocation (Math|Vector|MakeVector {sl[0]} {sl[1]} {sl[2]}))
  (for r (Actor|GetAllActorswithTag :Tag "RainOn")
    (Rendering|SetVisibility :self (Variables|Default|GetRain) :bNewVisibility true :bPropagateToChildren false)))
"""
    return str(TG.run(CH, code, clear=False))[:200]

def night():
    out = {}
    for a in E.get_all_level_actors():
        lab = a.get_actor_label()
        if isinstance(a, unreal.DirectionalLight):
            c = a.light_component; out["sun_was"] = c.get_editor_property("intensity")
            c.set_editor_property("intensity", 0.35); c.set_light_color(unreal.LinearColor(0.55, 0.65, 1.0, 1.0))
            a.set_actor_rotation(unreal.Rotator(roll=0, pitch=-35, yaw=40), False)
        if isinstance(a, unreal.SkyLight):
            c = a.light_component; out["sky_was"] = c.get_editor_property("intensity"); c.set_editor_property("intensity", 0.12)
        if isinstance(a, unreal.PostProcessVolume):
            s = a.get_editor_property("settings")
            for k, v in (("override_auto_exposure_min_brightness", True), ("auto_exposure_min_brightness", 0.6), ("override_auto_exposure_max_brightness", True), ("auto_exposure_max_brightness", 1.4),
                         ("override_auto_exposure_bias", True), ("auto_exposure_bias", -0.6), ("override_vignette_intensity", True), ("vignette_intensity", 0.75)):
                try: s.set_editor_property(k, v)
                except Exception as e: out["pp_" + k] = str(e)[:50]
            a.set_editor_property("settings", s)
        if isinstance(a, unreal.ExponentialHeightFog):
            c = a.component
            try: c.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.05, 0.06, 0.08, 1.0))
            except Exception: pass
        if lab == "Sky_Dome": a.set_actor_hidden_in_game(True)
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() in ("RainOn_Marker",) or a.get_actor_label().startswith("Torch_"): E.destroy_actor(a)
    tp = E.spawn_actor_from_class(unreal.TargetPoint, V(0, 0, -9000)); tp.tags = [unreal.Name("RainOn")]; tp.set_actor_label("RainOn_Marker"); tp.set_folder_path("UI")
    random.seed(77); obs = M.obstacles(); pole = EAL.load_asset(M.POLE); fire = EAL.load_asset("/Game/Effects/Flames/NS_Fire")
    ph, pb = M.height(M.POLE); s = 230.0 / max(ph, 1)
    pts = []; tries = 0
    while len(pts) < 26 and tries < 3000:
        tries += 1
        x = random.uniform(-500, 9900); y = random.uniform(-4300, 4300)
        if any(M.inside(x, y, b, 120) for b in obs) or any(math.hypot(x - a_, y - b_) < 1100 for a_, b_ in pts): continue
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        z = M.ground_z(x, y) or 0.0
        p = E.spawn_actor_from_object(pole, V(x, y, z - pb.min.z * s)); p.set_actor_scale3d(V(s * 0.7, s * 0.7, s))
        p.static_mesh_component.set_collision_profile_name("BlockAll"); p.set_actor_label(f"Torch_{i}_Pole"); p.set_folder_path("Art/War/Torches")
        f = E.spawn_actor_from_class(unreal.NiagaraActor, V(x, y, z + 238)); f.niagara_component.set_asset(fire); f.set_actor_scale3d(V(0.35, 0.35, 0.45))
        f.set_actor_label(f"Torch_{i}_Fire"); f.set_folder_path("Art/War/Torches")
        l = E.spawn_actor_from_class(unreal.PointLight, V(x, y, z + 250)); lc = l.point_light_component
        lc.set_intensity(9000.0); lc.set_light_color(unreal.LinearColor(1.0, 0.55, 0.22, 1.0)); lc.set_attenuation_radius(1400.0); lc.set_cast_shadows(False)
        l.set_actor_label(f"Torch_{i}_Light"); l.set_folder_path("Art/War/Torches")
    out["torches"] = len(pts)
    L.save_current_level(); return out

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    L.load_level(f"{R}/Maps/M_Cut_WarField")
    step("mat", rain_material); step("rain", rain_component); step("night", night)
    return res
