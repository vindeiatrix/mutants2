import contextlib
import io

from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.ui.theme import yellow


def _ctx(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"
    w = world_mod.World()
    w.year(2000)
    w.room_description = lambda *args, **kwargs: "You are here."
    p = Player(year=2000, clazz="Warrior", ions=100000)
    save = persistence.Save()
    ctx = make_context(p, w, save)
    return ctx, w


def test_render_gating(tmp_path):
    ctx, w = _ctx(tmp_path)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("east")
    out = buf.getvalue()
    assert "You are here." in out and "Compass:" in out

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("travel 2101")
    out = buf.getvalue()
    assert yellow("ZAAAAPPPPP!! You've been sent to the year 2100 A.D.") in out
    assert "You are here." not in out and "Compass" not in out

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("look")
    out = buf.getvalue()
    assert "You are here." in out and "Compass:" in out
