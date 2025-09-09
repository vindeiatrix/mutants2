import contextlib
import io
import re

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_debug_set_riblets(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"
    w = world_mod.World(global_seed=42)
    w.year(2000)
    p = Player(year=2000, clazz="Warrior")
    save = persistence.Save()
    ctx = make_context(p, w, save, dev=True)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("debug set riblet 4242")
    out = strip_ansi(buf.getvalue())
    assert "Riblets set to 4242." in out
    assert p.riblets == 4242
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("help debug")
    out = buf.getvalue()
    assert "debug set riblet <N>" in out
