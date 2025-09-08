import contextlib
import io

from mutants2.engine import persistence, world as world_mod
from mutants2.engine.world import HIGHEST_CENTURY
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.ui.theme import yellow


def _ctx(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"
    w = world_mod.World()
    p = Player(clazz="Warrior", ions=100000)
    save = persistence.Save()
    ctx = make_context(p, w, save)
    return ctx


def test_travel_rounding_and_bounds(tmp_path):
    ctx = _ctx(tmp_path)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("travel 2342")
    out = buf.getvalue()
    assert yellow("ZAAAAPPPPP!! You've been sent to the year 2300 A.D.") in out

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("travel 1999")
    out = buf.getvalue()
    assert yellow(f"You can only travel from year 2000 to {HIGHEST_CENTURY}!") in out

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("travel 3001")
    out = buf.getvalue()
    assert yellow(f"You can only travel from year 2000 to {HIGHEST_CENTURY}!") in out
