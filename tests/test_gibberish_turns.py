import contextlib
from io import StringIO

import pytest

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


@pytest.fixture
def cli(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player()
    p.clazz = "Warrior"
    w = world_mod.World()
    w.year(2000)
    w.place_monster(2000, 0, 2, "mutant")
    w.monster_here(2000, 0, 2)["aggro"] = True
    ctx = make_context(p, w, save)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


def test_gibberish_consumes_turn(cli):
    out = cli.run(["asdf"])
    assert "You're asdfing!" in out
    assert "footsteps" in out.lower()
