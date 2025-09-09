import contextlib
import io
import re
import tempfile
from pathlib import Path

from mutants2.cli.shell import make_context
from mutants2.engine import world as world_mod, persistence
from mutants2.engine.player import Player
from mutants2.ui.render import render_single_exit
from mutants2.ui.theme import COLOR_HEADER, COLOR_ITEM, green, red


def run_look() -> list[str]:
    save = persistence.Save(global_seed=42)
    w = world_mod.World(global_seed=42)
    w.year(2000)
    w.set_ground_item(2000, 0, 0, "skull")
    p = Player(year=2000, clazz="Warrior", ions=100000)
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            ctx.dispatch_line("look")
    return buf.getvalue().splitlines()


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip(s: str) -> str:
    return ANSI_RE.sub("", s)


def test_room_colors_smoke() -> None:
    lines = run_look()
    # 0 = command echo; 1 = header; 2 = compass
    assert lines[1] == red(strip(lines[1]))
    assert lines[2] == green("Compass: (0E : 0N)")

    exits = [
        render_single_exit(d, "area continues.")
        for d in ("north", "south", "east", "west")
    ]
    assert lines[3:7] == exits

    assert lines[7] == COLOR_HEADER("On the ground lies:")
    assert lines[8] == COLOR_ITEM("A Skull.")
