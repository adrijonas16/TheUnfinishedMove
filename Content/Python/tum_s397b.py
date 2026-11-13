# Goal = glowing ground ring + small pole (touch it to finish the cut), real top-down map in the corner (baked capture) instead of the bar,
# opening catapult stone that lands near the player and leaves a crater
import unreal, importlib, traceback, math, random
import tum_graph as TG; importlib.reload(TG)
import tum_s335 as M; importlib.reload(M)
import tum_s364b as S; importlib.reload(S)
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = M.E; L = M.L; V = unreal.Vector; R = "/Game/TUM"; UI = f"{R}/Materials/UI"; HUD = f"{R}/Core/BP_ObjectiveHUD"
res = {"ok": [], "err": {}}
def step(n, fn):
    try: r = fn(); res["ok"].append(n); res[n] = r
    except Exception: res["err"][n] = traceback.format_exc()[-1500:]
g = lambda n: f"(Variables|Default|Get{n})"
PL = "(Game|GetPlayerCharacter 0)"
def X(m, cls, x, y): return MEL.create_material_expression(m, cls, x, y)
def C(a, ao, b, bi): MEL.connect_material_expressions(a, ao, b, bi)

def materials():
    out = {}
    # ground ring decal (soft amber, not a beam of light)
    p = f"{UI}/M_GoalRing"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_GoalRing", UI, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
    try: m.set_editor_property("decal_blend_mode", unreal.DecalBlendMode.DBM_TRANSLUCENT)
    except Exception: pass
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    uv = X(m, unreal.MaterialExpressionTextureCoordinate, -900, 0)
    ctr = X(m, unreal.MaterialExpressionConstant2Vector, -900, 120); ctr.set_editor_property("r", 0.5); ctr.set_editor_property("g", 0.5)
    dist = X(m, unreal.MaterialExpressionDistance, -700, 40); C(uv, "", dist, "A"); C(ctr, "", dist, "B")
    sub = X(m, unreal.MaterialExpressionSubtract, -550, 40); sub.set_editor_property("const_b", 0.42); C(dist, "", sub, "A")
    ab = X(m, unreal.MaterialExpressionAbs, -420, 40); C(sub, "", ab, "")
    mul = X(m, unreal.MaterialExpressionMultiply, -300, 40); mul.set_editor_property("const_b", 22.0); C(ab, "", mul, "A")
    om = X(m, unreal.MaterialExpressionOneMinus, -180, 40); C(mul, "", om, "")
    sat = X(m, unreal.MaterialExpressionSaturate, -80, 40); C(om, "", sat, "")
    # faint filled disc inside the ring
    sub2 = X(m, unreal.MaterialExpressionSubtract, -550, 220); sub2.set_editor_property("const_a", 0.42); C(dist, "", sub2, "B")
    sat2 = X(m, unreal.MaterialExpressionSaturate, -420, 220); C(sub2, "", sat2, "")
    m2 = X(m, unreal.MaterialExpressionMultiply, -300, 220); m2.set_editor_property("const_b", 0.6); C(sat2, "", m2, "A")
    add = X(m, unreal.MaterialExpressionAdd, 40, 120); C(sat, "", add, "A"); C(m2, "", add, "B")
    col = X(m, unreal.MaterialExpressionConstant3Vector, -200, -200); col.set_editor_property("constant", unreal.LinearColor(1.0, 0.55, 0.18, 1))
    em = X(m, unreal.MaterialExpressionMultiply, 160, -120); C(col, "", em, "A"); C(sat, "", em, "B")
    em2 = X(m, unreal.MaterialExpressionMultiply, 300, -120); em2.set_editor_property("const_b", 3.0); C(em, "", em2, "A")
    MEL.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(em2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(add, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); out["ring"] = "ok"
    # crater decal: dark scorched earth with a soft edge
    p = f"{UI}/M_Crater"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_Crater", UI, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    try: m.set_editor_property("decal_blend_mode", unreal.DecalBlendMode.DBM_TRANSLUCENT)
    except Exception: pass
    uv = X(m, unreal.MaterialExpressionTextureCoordinate, -900, 0)
    ctr = X(m, unreal.MaterialExpressionConstant2Vector, -900, 120); ctr.set_editor_property("r", 0.5); ctr.set_editor_property("g", 0.5)
    dist = X(m, unreal.MaterialExpressionDistance, -700, 40); C(uv, "", dist, "A"); C(ctr, "", dist, "B")
    mul = X(m, unreal.MaterialExpressionMultiply, -550, 40); mul.set_editor_property("const_b", 2.2); C(dist, "", mul, "A")
    om = X(m, unreal.MaterialExpressionOneMinus, -420, 40); C(mul, "", om, "")
    sat = X(m, unreal.MaterialExpressionSaturate, -300, 40); C(om, "", sat, "")
    col = X(m, unreal.MaterialExpressionConstant3Vector, -300, -200); col.set_editor_property("constant", unreal.LinearColor(0.035, 0.028, 0.022, 1))
    MEL.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(sat, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); out["crater"] = "ok"
    # minimap material: unlit, always on top, texture param
    p = f"{UI}/M_Minimap"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset("M_Minimap", UI, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("two_sided", True)
    try: m.set_editor_property("disable_depth_test", True)
    except Exception: pass
    t = X(m, unreal.MaterialExpressionTextureSampleParameter2D, -500, 0); t.set_editor_property("parameter_name", "Map")
    t.set_editor_property("texture", EAL.load_asset("/Engine/EngineResources/DefaultTexture"))
    br = X(m, unreal.MaterialExpressionMultiply, -250, 0); br.set_editor_property("const_b", 1.15); C(t, "RGB", br, "A")
    op = X(m, unreal.MaterialExpressionScalarParameter, -250, 200); op.set_editor_property("parameter_name", "Opacity"); op.set_editor_property("default_value", 0.9)
    MEL.connect_material_property(br, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.recompile_material(m); EAL.save_loaded_asset(m, False); out["map"] = "ok"
    return out

def vec(base, *terms):
    comps = []
    for ax in ("x", "y", "z"):
        s = f"(.{ax} {base})"
        for v, k in terms: s = f"(+ {s} (* (.{ax} {v}) {k}))"
        comps.append(s)
    return f"(Math|Vector|MakeVector {comps[0]} {comps[1]} {comps[2]})"
def place(tag, loc, scale, look=False):
    rot = "(Math|Rotator|FindLookatRotation :Start p :Target cl)" if look else "cr"
    return (f'  (for m{tag} (Actor|GetAllActorswithTag :Tag "{tag}")\n'
            f'    (Transformation|SetActorLocationAndRotation :self m{tag} :NewLocation {loc} :NewRotation {rot} :bTeleport true)\n'
            f'    (Transformation|SetActorScale3D :self m{tag} :NewScale3D {scale}))\n')

def hud():
    TG.ensure_vars(HUD, [("Stage", "int"), ("bFactory", "bool"), ("Dist", "float"), ("Drop", "float"), ("StartDist", "float"),
                         ("MapCX", "float"), ("MapCY", "float"), ("MapHalf", "float")], objs=[("GoalActor", unreal.Actor.static_class())])
    hints = "\n".join(f'  (for h{n} (Actor|GetAllActorswithTag :Tag "HUDS{n}") (Rendering|SetActorHiddenInGame :self h{n} :bNewHidden (not (== {g("Stage")} {n}))))' for n in range(4))
    goals = "\n".join(f'  (for q{n} (Actor|GetAllActorswithTag :Tag "GoalS{n}") (if (== {g("Stage")} {n}) (Variables|Default|SetGoalActor q{n})))' for n in range(4))
    GP = "(Utilities|Casting|CastToBP_GameProgress :Object (Game|GetGameInstance))"
    S3 = lambda k: f"(Math|Vector|MakeVector {k} {k} {k})"
    # world point -> map point: world +X goes up, world +Y goes right
    def mp(wx, wy):
        return vec('c', ('rv', f"(* side (/ (- {wy} {g('MapCY')}) (* 2.0 {g('MapHalf')})))"), ('u', f"(* side (/ (- {wx} {g('MapCX')}) (* 2.0 {g('MapHalf')})))"), ('f', '-0.05'))
    code = f"""
(event EventBeginPlay
  (Variables|Default|SetStage 0)
  (bind gi {GP}
    (:then
      (if {g('Factory')}
        (if (Class|BPGameProgress|GetDragonDone :self gi) (Variables|Default|SetStage 1))
        (if (Class|BPGameProgress|GetWarDone :self gi) (Variables|Default|SetStage 2))
        (if (Class|BPGameProgress|GetCliffDone :self gi) (Variables|Default|SetStage 3)))
      (CallFunction|Setup))
    (:CastFailed (CallFunction|Setup))))

(event Custom|Setup
{hints}
  (for q (Actor|GetAllActorswithTag :Tag "Goal") (Variables|Default|SetGoalActor q))
{goals})

(event EventTick (DeltaSeconds)
  (bind cm (Game|GetPlayerCameraManager 0))
  (bind cl (Camera|GetCameraLocation :self cm))
  (bind cr (Camera|GetCameraRotation :self cm))
  (bind f (Math|Vector|GetForwardVector :InRot cr))
  (bind u (Math|Vector|GetUpVector :InRot cr))
  (bind rv (Math|Vector|GetRightVector :InRot cr))
  (bind p {vec('cl', ('f', g('Dist')), ('u', g('Drop')))})
  (for t (Actor|GetAllActorswithTag :Tag "HUDText")
    (Transformation|SetActorLocationAndRotation :self t :NewLocation p :NewRotation (Math|Rotator|FindLookatRotation :Start p :Target cl) :bTeleport true))
  (bind hw (* {g('Dist')} (Math|Trig|Tan(Degrees) (* (Camera|GetFOVAngle :self cm) 0.5))))
  (bind side (* hw 0.42))
  (bind c {vec('cl', ('f', g('Dist')), ('u', '(* hw 0.33)'), ('rv', '(* hw 0.72)'))})
  (bind pp (Transformation|GetActorLocation :self {PL}))
  (bind gl (Transformation|GetActorLocation :self {g('GoalActor')}))
{place('MapPanel', 'c', "(Math|Vector|MakeVector 0.0005 (/ side 100.0) (/ side 100.0))")}
{place('MapFrame', vec('c', ('f', '0.05')), "(Math|Vector|MakeVector 0.0005 (/ (* side 1.06) 100.0) (/ (* side 1.06) 100.0))")}
{place('MapGoal', mp('(.x gl)', '(.y gl)'), S3('(/ (* hw 0.022) 100.0)'))}
{place('MapYou', mp('(.x pp)', '(.y pp)'), S3('(/ (* hw 0.02) 100.0)'))}
  (for ml (Actor|GetAllActorswithTag :Tag "MapLabel")
    (Transformation|SetActorLocationAndRotation :self ml :NewLocation {vec('c', ('u', '(* side -0.56)'))} :NewRotation (Math|Rotator|FindLookatRotation :Start p :Target cl) :bTeleport true)
    (Transformation|SetActorScale3D :self ml :NewScale3D {S3('(/ hw 34.0)')})))
"""
    r = TG.run(HUD, code, events=["Setup"], clear=True)
    b = EAL.load_asset(HUD)
    for n in ("bFactory", "MapCX", "MapCY", "MapHalf"): BEL.set_blueprint_variable_instance_editable(b, n, True)
    BEL.compile_blueprint(b); cdo = unreal.get_default_object(b.generated_class())
    cdo.set_editor_property("Dist", 70.0); cdo.set_editor_property("Drop", -27.0); cdo.set_editor_property("MapHalf", 5000.0)
    EAL.save_loaded_asset(b, False); return str(r)[:300]

def catapult_bp():
    import tum_s374 as C4; importlib.reload(C4)
    import inspect
    src = inspect.getsource(C4.catapult_bp)
    src = src.replace('("Cat", unreal.StaticMeshActor.static_class())])', '("Cat", unreal.StaticMeshActor.static_class()), ("Crater", unreal.Actor.static_class())] + [("bFirst", "bool")])') if False else src
    src = src.replace('objs=[("Rock"', 'objs=[("Crater", unreal.Actor.static_class()), ("Rock"')
    src = src.replace('[("Fly", "bool")]', '[("Fly", "bool"), ("bOpener", "bool"), ("Shots", "int")]')
    src = src.replace("(Niagara|SpawnSystematLocation :SystemTemplate {g('Dust')} :Location tg)",
        "(Niagara|SpawnSystematLocation :SystemTemplate {g('Dust')} :Location tg :Scale (Math|Vector|MakeVector 1.6 1.6 1.6))\n      (Transformation|SetActorLocation :self {g('Crater')} :NewLocation (Math|Vector|MakeVector {g('TX')} {g('TY')} 0.0) :bTeleport true)\n      (Variables|Default|SetShots (+ {g('Shots')} 1))")
    src = src.replace("(Variables|Default|SetTX (+ (.x pl) (Math|Random|RandomFloatinRange :Min 450.0 :Max 1500.0)))\n        (Variables|Default|SetTY (+ (.y pl) (Math|Random|RandomFloatinRange :Min -800.0 :Max 800.0)))",
        "(if (and {g('Opener')} (== {g('Shots')} 0))\n          (Variables|Default|SetTX (+ (.x pl) 420.0))\n          (Variables|Default|SetTY (+ (.y pl) 160.0))\n          (else\n            (Variables|Default|SetTX (+ (.x pl) (Math|Random|RandomFloatinRange :Min 450.0 :Max 1500.0)))\n            (Variables|Default|SetTY (+ (.y pl) (Math|Random|RandomFloatinRange :Min -800.0 :Max 800.0)))))")
    src = src.replace('["Rock", "Launch", "Impact", "Dust", "Trail", "Cat", "Next"]', '["Rock", "Launch", "Impact", "Dust", "Trail", "Cat", "Next", "Crater", "bOpener"]')
    ns = dict(C4.__dict__); exec(src, ns); return ns["catapult_bp"]()

def goal_marker(name, x, y, z=None, trigger=None, tags=("Goal",), folder="Gameplay/Goal"):
    if z is None: z = M.ground_z(x, y) or 0.0
    out = []
    d = E.spawn_actor_from_class(unreal.DecalActor, V(x, y, z + 20), unreal.Rotator(roll=0, pitch=-90, yaw=0))
    dc = d.decal; dc.set_decal_material(EAL.load_asset(f"{UI}/M_GoalRing")); dc.set_editor_property("decal_size", V(120, 170, 170))
    d.set_actor_label(f"{name}_Ring"); d.set_folder_path(folder); out.append(d)
    pole = E.spawn_actor_from_object(EAL.load_asset(M.POLE), V(x, y, z)); ph, pb = M.height(M.POLE); s = 190.0 / max(ph, 1)
    pole.set_actor_scale3d(V(s * 0.6, s * 0.6, s)); pole.set_actor_location(V(x, y, z - pb.min.z * s), False, False)
    pole.static_mesh_component.set_collision_profile_name("NoCollision"); pole.set_actor_label(f"{name}_Pole"); pole.set_folder_path(folder)
    lh, lb = M.height(M.LANT[0]); ls = 26.0 / max(lh, 1.0)
    for i_, lm in enumerate(M.LANT):
        la = E.spawn_actor_from_object(EAL.load_asset(lm), V(x, y, z + 190 - lb.min.z * ls)); la.set_actor_scale3d(V(ls, ls, ls))
        la.static_mesh_component.set_collision_profile_name("NoCollision"); la.set_actor_label(f"{name}_Lamp{i_}"); la.set_folder_path(folder)
    lt = E.spawn_actor_from_class(unreal.PointLight, V(x, y, z + 200)); lc = lt.point_light_component
    lc.set_intensity(350.0); lc.set_light_color(unreal.LinearColor(1, 0.55, 0.2, 1)); lc.set_attenuation_radius(260.0); lc.set_cast_shadows(False)
    lt.set_actor_label(f"{name}_Glow"); lt.set_folder_path(folder)
    tp = E.spawn_actor_from_class(unreal.TargetPoint, V(x, y, z + 100)); tp.tags = list(tags); tp.set_actor_label(f"{name}_Goal"); tp.set_folder_path(folder)
    if trigger:
        t = E.spawn_actor_from_class(EAL.load_asset(f"{R}/Core/BP_Trigger").generated_class(), V(x, y, z + 90))
        for k, v in trigger.items(): t.set_editor_property(k, v)
        t.set_actor_label(f"{name}_Trigger"); t.set_folder_path(folder)
    return round(z)

def map_actors(cx, cy, half, mapname):
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(("Map_", "MapCapture")) or isinstance(a, unreal.SceneCapture2D): E.destroy_actor(a)
    # bake a top-down picture of this map into a texture
    rt = unreal.RenderingLibrary.create_render_target2d(M.world(), 1024, 1024, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = E.spawn_actor_from_class(unreal.SceneCapture2D, V(cx, cy, 9000), unreal.Rotator(roll=0, pitch=-90, yaw=0))
    sc = cap.capture_component2d
    sc.set_editor_property("projection_type", unreal.CameraProjectionMode.ORTHOGRAPHIC); sc.set_editor_property("ortho_width", half * 2)
    sc.set_editor_property("texture_target", rt); sc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    sc.set_editor_property("capture_every_frame", False); sc.set_editor_property("capture_on_movement", False)
    for hide in [a for a in E.get_all_level_actors() if a.get_actor_label().startswith(("Sky_Dome", "Bound_", "Horizon_"))]:
        try: sc.hide_actor_components(hide, False)
        except Exception: pass
    sc.capture_scene()
    tex_name = f"T_Map_{mapname}"; tp = f"{UI}/{tex_name}"
    D = r"C:\UnrealProjects\TheUnfinishedMove\SourceArt\maps"
    import os; os.makedirs(D, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(M.world(), rt, D, tex_name + ".png")
    it = unreal.AssetImportTask(); it.filename = os.path.join(D, tex_name + ".png"); it.destination_path = UI; it.automated = True; it.save = True; it.replace_existing = True
    AT.import_asset_tasks([it])
    tx = EAL.load_asset(tp)
    if tx:
        tx.set_editor_property("srgb", True); tx.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
        tx.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI); EAL.save_loaded_asset(tx, False)
    E.destroy_actor(cap)
    mi_p = f"{UI}/MI_Map_{mapname}"
    mi = EAL.load_asset(mi_p) if EAL.does_asset_exist(mi_p) else AT.create_asset(f"MI_Map_{mapname}", UI, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, EAL.load_asset(f"{UI}/M_Minimap")); MEL.set_material_instance_texture_parameter_value(mi, "Map", EAL.load_asset(tp)); EAL.save_loaded_asset(mi, False)
    def m(shape, mat, tag):
        a = E.spawn_actor_from_class(unreal.StaticMeshActor, V(0, 0, -9000), unreal.Rotator())
        c = a.static_mesh_component; c.set_mobility(unreal.ComponentMobility.MOVABLE); c.set_static_mesh(EAL.load_asset(f"/Engine/BasicShapes/{shape}"))
        c.set_material(0, mat); c.set_collision_profile_name("NoCollision"); c.set_cast_shadow(False); a.set_actor_enable_collision(False)
        try: c.set_editor_property("translucency_sort_priority", {"MapFrame": 0, "MapPanel": 1, "MapGoal": 2, "MapYou": 3}[tag])
        except Exception: pass
        a.tags = [tag]; a.set_actor_label(f"Map_{tag}"); a.set_folder_path("UI/Map")
    m("Cube", EAL.load_asset(f"{UI}/MI_Map_Bar"), "MapFrame"); m("Cube", mi, "MapPanel")
    m("Sphere", EAL.load_asset(f"{UI}/MI_Map_Goal"), "MapGoal"); m("Sphere", EAL.load_asset(f"{UI}/MI_Map_You"), "MapYou")
    t = E.spawn_actor_from_class(unreal.TextRenderActor, V(0, 0, -9000), unreal.Rotator()); t.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    tc = t.text_render; tc.set_text(unreal.Text("MAP")); tc.set_world_size(1.0)
    tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER); tc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_TOP)
    tc.set_text_render_color(unreal.Color(r=235, g=215, b=185, a=255)); tc.set_cast_shadow(False)
    try: tc.set_text_material(EAL.load_asset(f"{R}/Materials/M_TextGlow"))
    except Exception: pass
    t.tags = ["MapLabel"]; t.set_actor_label("Map_Label"); t.set_folder_path("UI/Map")
    for a in E.get_all_level_actors():
        if a.get_actor_label() == "ObjectiveHUD":
            a.set_editor_property("MapCX", float(cx)); a.set_editor_property("MapCY", float(cy)); a.set_editor_property("MapHalf", float(half))
    return tp

def clear_cp(prefix):
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label().startswith(prefix): E.destroy_actor(a)

def war():
    out = {}
    clear_cp(("CP_War", "Goal_War"))
    out["goal"] = goal_marker("Goal_War", 5650, -330, trigger={"Radius": 140.0, "bOpenMap": True, "TargetMap": "M_FactoryHub", "Flag": 2, "bStartDisabled": False})
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() in ("Seal_Take", "Rope_Cut", "Shrine_Light"): E.destroy_actor(a)
    # crater per catapult + the opener
    cr = EAL.load_asset(f"{UI}/M_Crater"); stones = M.ROCKS
    for i in range(3):
        clear_cp((f"Crater_{i}",))
        root = E.spawn_actor_from_class(unreal.Actor, V(0, 0, -5000)) if False else E.spawn_actor_from_class(unreal.DecalActor, V(0, 0, -5000), unreal.Rotator(roll=0, pitch=-90, yaw=0))
        root.decal.set_decal_material(cr); root.decal.set_editor_property("decal_size", V(150, 190, 190)); root.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        root.set_actor_label(f"Crater_{i}"); root.set_folder_path("Art/War/Battle/Catapults")
        for k in range(7):
            ang = k / 7 * 6.283 + random.uniform(-0.3, 0.3); rr = random.uniform(120, 175)
            s = E.spawn_actor_from_object(EAL.load_asset(random.choice(stones)), V(math.cos(ang) * rr, math.sin(ang) * rr, -5000), unreal.Rotator(roll=0, pitch=0, yaw=random.uniform(0, 360)))
            s.set_actor_scale3d(V(*(random.uniform(0.25, 0.45),) * 3)); s.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            s.static_mesh_component.set_collision_profile_name("NoCollision"); s.set_actor_enable_collision(False)
            s.attach_to_actor(root, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
            s.set_actor_label(f"Crater_{i}_Rubble{k}"); s.set_folder_path("Art/War/Battle/Catapults")
        for a in E.get_all_level_actors():
            if a.get_actor_label() == f"Catapult_{i}_Ctl":
                a.set_editor_property("Crater", root); a.set_editor_property("bOpener", i == 0)
                if i == 0: a.set_editor_property("Next", 1.3)
    out["map"] = map_actors(3200, 0, 4800, "War"); return out

def factory():
    clear_cp(("CP_F",))
    pts = {0: (3500, 140), 1: (5450, -420), 2: (6450, -430), 3: (8300, 160)}
    zs = {n: goal_marker(f"CP_F{n}", x, y, tags=(f"GoalS{n}",)) for n, (x, y) in pts.items()}
    return {"goals": zs, "map": map_actors(4700, 0, 5600, "Factory")}

def cliff():
    clear_cp(("CP_Cliff",))
    for a in list(E.get_all_level_actors()):
        if a.get_actor_label() == "Arch_Light": a.point_light_component.set_intensity(800.0)
    return {"goal": goal_marker("CP_Cliff", 5500, 260), "map": map_actors(2700, 0, 3600, "Cliff")}

def dragon():
    return {"map": map_actors(2400, 0, 11000, "Dragon")}

def run():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    step("materials", materials); step("hud", hud); step("catapult", catapult_bp)
    for mp, fn in (("M_Cut_WarField", war), ("M_FactoryHub", factory), ("M_Cut_Cliff", cliff), ("M_Cut_Dragon", dragon)):
        L.load_level(f"{R}/Maps/{mp}"); step(mp, fn); L.save_current_level()
    return res

def run_maps():
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(): raise RuntimeError("PIE running")
    for mp, args in (("M_Cut_WarField", (3200, 0, 4800, "War")), ("M_FactoryHub", (4700, 0, 5600, "Factory")), ("M_Cut_Cliff", (2700, 0, 3600, "Cliff")), ("M_Cut_Dragon", (2400, 0, 11000, "Dragon"))):
        L.load_level(f"{R}/Maps/{mp}"); step(mp, lambda: map_actors(*args)); L.save_current_level()
    return res
