import contextlib
from io import StringIO

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


def test_question_help_alias(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    w = world_mod.World()
    p = Player()
    save = persistence.Save()
    ctx = make_context(p, w, save)
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("?")
    out = buf.getvalue()
    assert "Commands:" in out
    assert w.turn == 0
