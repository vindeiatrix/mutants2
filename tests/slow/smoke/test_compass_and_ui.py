import contextlib
import io
import re
import tempfile
from pathlib import Path

from mutants2.cli.shell import make_context
from mutants2.engine import world as world_mod, persistence
from mutants2.engine.player import Player


def run_commands(cmds):
    save = persistence.Save(global_seed=42)
    w = world_mod.World(global_seed=42)
    w.year(2000)
    p = Player(year=2000, clazz="Warrior")
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            for c in cmds:
                ctx.dispatch_line(c)
    out = buf.getvalue()
    buf.close()
    return re.sub(r"\x1b\[[0-9;]*m", "", out)


def test_compass_south_then_look():
    out = run_commands(["s", "look"])
    assert "Compass: (0E : -1N)" in out


def test_compass_north_then_look():
    out = run_commands(["n", "look"])
    assert "Compass: (0E : 1N)" in out


def test_single_command_echo():
    out = run_commands(["look"])
    lines = out.strip().splitlines()
    assert lines.count("look") == 1


def test_resident_and_arrival_rendering():
    save = persistence.Save(global_seed=42)
    w = world_mod.World(global_seed=42)
    w.year(2000)
    p = Player(year=2000, clazz="Warrior")
    w.place_monster(2000, 0, 0, "night_stalker")
    w.place_monster(2000, 1, 0, "mutant")
    w.monster_here(2000, 1, 0)["aggro"] = True
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            ctx.dispatch_line("look")
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    buf.close()
    assert out.splitlines().count("look") == 1
    assert re.search(r"Night-Stalker-\d{4} is here", out)
    assert not re.search(r"Mutant-\d{4} is here", out)
    assert "You see shadows" in out
    assert out.count("has just arrived from") == 1
    presence_idx = re.search(r"Night-Stalker-\d{4} is here", out).start()
    shadow_idx = out.find("You see shadows")
    arrival_idx = out.find("has just arrived from")
    assert presence_idx < shadow_idx < arrival_idx
