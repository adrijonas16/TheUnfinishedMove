# Editor-only bridge for Claude (The Unfinished Move, jam tooling).
# Runs automatically when the editor starts (Python Editor Script Plugin).
# Every ~1 s it executes any *.py dropped in <Project>/Saved/ClaudeQueue/ and writes <name>.log (JSON) next to it.
# Saved/ is git-ignored and this never runs in a packaged game.
import unreal, os, glob, json, time, traceback

_PROJ = os.path.abspath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
QUEUE = os.path.join(_PROJ, "Saved", "ClaudeQueue")
os.makedirs(QUEUE, exist_ok=True)
_state = {"last": 0.0, "busy": False}

def _beat():
    try:
        open(os.path.join(QUEUE, "heartbeat.json"), "w").write(json.dumps({"time": time.time(), "engine": unreal.SystemLibrary.get_engine_version()}))
    except Exception:
        pass

def _run(path):
    done = path + ".running"
    try:
        os.replace(path, done)
    except Exception:
        return
    res = {"file": os.path.basename(path), "ok": True, "error": "", "result": None, "start": time.time()}
    try:
        g = {"__name__": "__claude__", "__file__": done, "RESULT": None}
        exec(compile(open(done, encoding="utf-8").read(), path, "exec"), g)
        res["result"] = g.get("RESULT")
    except Exception:
        res["ok"] = False
        res["error"] = traceback.format_exc()[-4000:]
    res["seconds"] = round(time.time() - res["start"], 2)
    open(path[:-3] + ".log", "w", encoding="utf-8").write(json.dumps(res, indent=1, default=str))
    try:
        os.replace(done, path + ".done")
    except Exception:
        pass

def _tick(dt):
    now = time.time()
    if _state["busy"] or now - _state["last"] < 1.0:
        return
    _state["last"] = now
    _state["busy"] = True
    try:
        _beat()
        if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
            return          # never edit assets while Play-In-Editor is running; queued scripts wait
        for f in sorted(glob.glob(os.path.join(QUEUE, "*.py"))):
            _run(f)
    finally:
        _state["busy"] = False

unreal.register_slate_post_tick_callback(_tick)
unreal.log("Claude bridge listening on " + QUEUE)
