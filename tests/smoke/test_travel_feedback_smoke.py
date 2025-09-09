import contextlib
import io
import tempfile
from pathlib import Path

from mutants2.cli.shell import make_context
from mutants2.engine import world as world_mod, persistence
from mutants2.engine.player import Player
from mutants2.ui.theme import COLOR_HEADER


def run_travel() -> list[str]:
    save = persistence.Save(global_seed=42)
    w = world_mod.World(global_seed=42)
    w.year(2000)
    p = Player(year=2000, clazz="Warrior", ions=100000)
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            ctx.dispatch_line("travel 2342")
    return buf.getvalue().splitlines()


def test_travel_feedback_smoke() -> None:
    lines = run_travel()
    assert lines[1] == COLOR_HEADER(
        "ZAAAAPPPPP!! You've been sent to the year 2300 A.D."
    )
    assert all("Compass:" not in ln for ln in lines[2:])
