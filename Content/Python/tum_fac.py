# Factory kit: boxes and bars from the engine cube with triplanar (world-aligned) materials, so nothing can stretch.
# Steel columns, trusses, window walls, catwalk decks, railings and stairs are assembled from these.
import unreal, math
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); V = unreal.Vector
CUBE = "/Engine/BasicShapes/Cube"; MS = "/Game/TUM/Materials/Surfaces"; DCS = "/Game/DerelictCorridor/Assets/Fab/Megascans/Surfaces"
TAG = "FAC2"; _c = {}
def asset(p):
    if p not in _c: _c[p] = EAL.load_asset(p)
    return _c[p]
def mi(name, src, folder=None, tile=None, rough=None, metal=None, tint=None):
    """Triplanar MI: a copy of an existing MI_W_* with other textures / values."""
    p = f"{MS}/MI_W_{name}"
    if not EAL.does_asset_exist(p): EAL.duplicate_asset(f"{MS}/MI_W_{src}", p)
    x = EAL.load_asset(p)
    if folder:
        for k, suf in (("BaseColor", "_B"), ("Normal", "_N"), ("ORM", "_ORM")):
            tp = f"{DCS}/{folder}/T_{folder}{suf}"
            if EAL.does_asset_exist(tp): MEL.set_material_instance_texture_parameter_value(x, k, EAL.load_asset(tp))
    if tile is not None: MEL.set_material_instance_scalar_parameter_value(x, "TileSize", tile)
    if rough is not None: MEL.set_material_instance_scalar_parameter_value(x, "RoughnessMul", rough)
    if metal is not None: MEL.set_material_instance_scalar_parameter_value(x, "MetallicMul", metal)
    if tint is not None: MEL.set_material_instance_vector_parameter_value(x, "Tint", unreal.LinearColor(tint[0], tint[1], tint[2], 1))
    EAL.save_loaded_asset(x, False); _c[p] = x; return x
def glow(name, color, strength):
    p = f"{MS}/{name}"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m = AT.create_asset(name, MS, unreal.Material, unreal.MaterialFactoryNew()); m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    c = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -500, 0); c.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1))
    # dirty glass: brightness broken up by a tiling noise in object UVs
    t = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSample, -500, 200); t.set_editor_property("texture", EAL.load_asset("/Engine/EngineMaterials/T_Default_Material_Grid_M"))
    k = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -500, 420); k.set_editor_property("r", strength)
    lo = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 300); lo.set_editor_property("r", 0.55)
    hi = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 360); hi.set_editor_property("r", 1.0)
    lp = MEL.create_material_expression(m, unreal.MaterialExpressionLinearInterpolate, -150, 250)
    MEL.connect_material_expressions(lo, "", lp, "A"); MEL.connect_material_expressions(hi, "", lp, "B"); MEL.connect_material_expressions(t, "R", lp, "Alpha")
    m1 = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, 0, 100); MEL.connect_material_expressions(c, "", m1, "A"); MEL.connect_material_expressions(lp, "", m1, "B")
    m2 = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, 150, 100); MEL.connect_material_expressions(m1, "", m2, "A"); MEL.connect_material_expressions(k, "", m2, "B")
    MEL.connect_material_property(m2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR); MEL.recompile_material(m); EAL.save_loaded_asset(m, False); _c[p] = m; return m
def _fin(a, name, folder, mat, collide, tags, shadow):
    c = a.static_mesh_component
    if mat is not None: c.set_material(0, mat)
    if not collide: a.set_actor_enable_collision(False); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    if not shadow: c.set_cast_shadow(False)
    a.set_actor_label(name); a.set_folder_path(folder); a.tags = [unreal.Name(TAG)] + [unreal.Name(t) for t in tags]; return a
def box(name, x0, x1, y0, y1, z0, z1, mat, folder, collide=False, tags=(), shadow=True):
    a = E.spawn_actor_from_object(asset(CUBE), V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), unreal.Rotator())
    a.set_actor_scale3d(V(abs(x1 - x0) / 100, abs(y1 - y0) / 100, abs(z1 - z0) / 100)); return _fin(a, name, folder, mat, collide, tags, shadow)
def bar(name, p0, p1, w, h, mat, folder, collide=False, tags=(), shadow=True, roll=0.0):
    """A beam from p0 to p1 (w across, h tall)."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]; L = math.sqrt(dx * dx + dy * dy + dz * dz)
    rot = unreal.Rotator(roll=roll, pitch=math.degrees(math.atan2(dz, math.hypot(dx, dy))), yaw=math.degrees(math.atan2(dy, dx)))
    a = E.spawn_actor_from_object(asset(CUBE), V((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2), rot)
    a.set_actor_scale3d(V(L / 100, w / 100, h / 100)); return _fin(a, name, folder, mat, collide, tags, shadow)
def hcol(name, x, y, z0, z1, mat, folder, size=34, along_y=False, shadow=True):
    """H-section steel column: two flanges and a web."""
    f, t = size / 2, 4
    if along_y:
        box(name + "_a", x - f, x + f, y - f, y - f + t, z0, z1, mat, folder, shadow=shadow); box(name + "_b", x - f, x + f, y + f - t, y + f, z0, z1, mat, folder, shadow=shadow)
        box(name + "_w", x - t / 2, x + t / 2, y - f, y + f, z0, z1, mat, folder, shadow=False)
    else:
        box(name + "_a", x - f, x - f + t, y - f, y + f, z0, z1, mat, folder, shadow=shadow); box(name + "_b", x + f - t, x + f, y - f, y + f, z0, z1, mat, folder, shadow=shadow)
        box(name + "_w", x - f, x + f, y - t / 2, y + t / 2, z0, z1, mat, folder, shadow=False)
def railing(name, pts, mat, folder, h=105, post=140, collide_wall=True):
    """Posts + top and mid rail along a polyline of (x, y, z) deck-edge points; an invisible wall keeps the player in."""
    n = 0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; L = math.dist(a, b)
        if L < 1: continue
        k = max(1, int(round(L / post)))
        for j in range(k + 1):
            t = j / k; p = [a[q] + (b[q] - a[q]) * t for q in range(3)]
            if j == k and i < len(pts) - 2: continue
            box(f"{name}_p{n}", p[0] - 2.5, p[0] + 2.5, p[1] - 2.5, p[1] + 2.5, p[2], p[2] + h, mat, folder, shadow=False); n += 1
        for zz, th in ((h, 5), (h * 0.52, 3.5), (9, 9)):
            bar(f"{name}_r{i}_{int(zz)}", (a[0], a[1], a[2] + zz), (b[0], b[1], b[2] + zz), th, th if zz > 10 else 2, mat, folder, shadow=(zz == h))
        if collide_wall:
            w = bar(f"{name}_wall{i}", (a[0], a[1], a[2] + h / 2 + 20), (b[0], b[1], b[2] + h / 2 + 20), 6, h + 40, asset(f"{MS}/M_Invisible"), folder, collide=True, shadow=False)
            w.set_actor_hidden_in_game(True)
    return n
def deck(name, x0, x1, y0, y1, z, mat, edge_mat, folder, collide=False, thick=6, joist=120):
    """Catwalk deck: plate on steel joists with edge channels (top of the plate at z)."""
    box(name + "_plate", x0, x1, y0, y1, z - thick, z, mat, folder, collide=collide)
    lx = (x1 - x0) >= (y1 - y0)
    if lx:
        for i, y in enumerate((y0 + 4, y1 - 4)): box(f"{name}_edge{i}", x0, x1, y - 4, y + 4, z - 26, z - thick, edge_mat, folder)
        x = x0 + joist / 2
        while x < x1: box(f"{name}_j{int(x)}", x - 3, x + 3, y0 + 8, y1 - 8, z - 20, z - thick, edge_mat, folder, shadow=False); x += joist
    else:
        for i, x in enumerate((x0 + 4, x1 - 4)): box(f"{name}_edge{i}", x - 4, x + 4, y0, y1, z - 26, z - thick, edge_mat, folder)
        y = y0 + joist / 2
        while y < y1: box(f"{name}_j{int(y)}", x0 + 8, x1 - 8, y - 3, y + 3, z - 20, z - thick, edge_mat, folder, shadow=False); y += joist
def stairs(name, x0, x1, y0, y1, z0, z1, mat, edge_mat, folder, along="x", rise=20.0):
    """Open steel stair from (x0, z0) up to (x1, z1) along x (or y): treads + two stringers."""
    n = max(2, int(round(abs(z1 - z0) / rise)))
    if along == "x":
        run = (x1 - x0) / n
        for i in range(n):
            xa = x0 + i * run; z = z0 + (i + 1) * (z1 - z0) / n
            box(f"{name}_t{i}", min(xa, xa + run), max(xa, xa + run), y0 + 4, y1 - 4, z - 4, z, mat, folder, shadow=False)
        for i, y in enumerate((y0 + 2, y1 - 2)): bar(f"{name}_s{i}", (x0, y, z0 - 6), (x1, y, z1 - 6), 5, 24, edge_mat, folder)
    else:
        run = (y1 - y0) / n
        for i in range(n):
            ya = y0 + i * run; z = z0 + (i + 1) * (z1 - z0) / n
            box(f"{name}_t{i}", x0 + 4, x1 - 4, min(ya, ya + run), max(ya, ya + run), z - 4, z, mat, folder, shadow=False)
        for i, x in enumerate((x0 + 2, x1 - 2)): bar(f"{name}_s{i}", (x, y0, z0 - 6), (x, y1, z1 - 6), 5, 24, edge_mat, folder)
    return n
def truss(name, x, y0, y1, zb, zt, mat, folder, panel=260):
    """Parallel-chord roof truss across the hall at x."""
    bar(name + "_bot", (x, y0, zb), (x, y1, zb), 14, 14, mat, folder); bar(name + "_top", (x, y0, zt), (x, y1, zt), 14, 14, mat, folder)
    k = max(2, int(round((y1 - y0) / panel))); w = (y1 - y0) / k
    for i in range(k):
        a = y0 + i * w; b = a + w
        p0, p1 = ((x, a, zb), (x, b, zt)) if i % 2 == 0 else ((x, a, zt), (x, b, zb))
        bar(f"{name}_d{i}", p0, p1, 8, 8, mat, folder, shadow=False)
    for i in range(k + 1): bar(f"{name}_v{i}", (x, y0 + i * w, zb), (x, y0 + i * w, zt), 7, 7, mat, folder, shadow=False)
def window(name, x0, x1, y, z0, z1, glass, frame, folder, cols=4, rows=5, broken=(), dark=None):
    """Factory window in the wall plane y: one glowing dirty pane behind a steel mullion grid; broken panes are dark holes."""
    pw = (x1 - x0) / cols; ph = (z1 - z0) / rows
    box(name + "_glass", x0, x1, y - 1.5, y + 1.5, z0, z1, glass, folder, shadow=False)
    for (c, r) in broken:
        if dark is not None: box(f"{name}_hole{c}{r}", x0 + c * pw, x0 + (c + 1) * pw, y - 3, y + 3, z0 + r * ph, z0 + (r + 1) * ph, dark, folder, shadow=False)
    for c in range(cols + 1): box(f"{name}_m{c}", x0 + c * pw - 3.5, x0 + c * pw + 3.5, y - 5, y + 5, z0, z1, frame, folder, shadow=False)
    for r in range(rows + 1): box(f"{name}_h{r}", x0, x1, y - 5, y + 5, z0 + r * ph - 3.5, z0 + r * ph + 3.5, frame, folder, shadow=False)
def clear(prefix=None):
    n = 0
    for a in list(E.get_all_level_actors()):
        if unreal.Name(TAG) in a.tags and (prefix is None or str(a.get_folder_path()).startswith(prefix)): E.destroy_actor(a); n += 1
    return n
