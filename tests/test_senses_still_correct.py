from io import StringIO
import contextlib

import pytest

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


@pytest.fixture
def world_two_adjacent_passive():
    w = world_mod.World()
    w.year(2000)
    for (x, y), _ in list(w.monsters_in_year(2000).items()):
        w.remove_monster(2000, x, y)
    w.place_monster(2000, 1, 0, "mutant")
    w.place_monster(2000, 0, 1, "mutant")
    return w


@pytest.fixture
def staged_world_aggro_east():
    w = world_mod.World()
    w.year(2000)
    for (x, y), _ in list(w.monsters_in_year(2000).items()):
        w.remove_monster(2000, x, y)
    w.place_monster(2000, 2, 0, "mutant")
    w.monster_here(2000, 2, 0)["aggro"] = True
    return w


@pytest.fixture
def cli(tmp_path, monkeypatch, world_two_adjacent_passive):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player()
    p.clazz = "Warrior"
    ctx = make_context(p, world_two_adjacent_passive, save)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


def test_shadows_adjacent_only(cli):
    out = cli.run(["look"])
    assert "shadows to the" in out.lower()


def test_arrival_after_chase(tmp_path, monkeypatch, staged_world_aggro_east):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player()
    p.clazz = "Warrior"
    ctx = make_context(p, staged_world_aggro_east, save)

    buf1 = StringIO()
    with contextlib.redirect_stdout(buf1):
        ctx.dispatch_line("loo")
    buf2 = StringIO()
    with contextlib.redirect_stdout(buf2):
        ctx.dispatch_line("loo")
    out2 = buf2.getvalue()
    assert "has just arrived from the west" in out2.lower()
    assert "is here" in out2.lower()

