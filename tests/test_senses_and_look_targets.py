import contextlib
from io import StringIO

import pytest

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


@pytest.fixture
def world():
    w = world_mod.World()
    w.year(2000)
    return w


@pytest.fixture
def cli(world, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    p = Player()
    p.clazz = "Warrior"
    save = persistence.Save()
    ctx = make_context(p, world, save)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


def test_shadow_adjacent_only(cli, world):
    world.place_monster(2000, 1, 0, "mutant")
    out = cli.run(["look"])
    assert "shadow flickers to the east" in out.lower()
    yr = world.year(2000)
    yr.grid.adj[(0, 0)].discard("east")
    yr.grid.adj[(1, 0)].discard("west")
    out = cli.run(["look"])
    assert "shadow flickers" not in out.lower()


def test_look_dir_and_blocked(cli):
    out = cli.run(["loo n"])
    assert "***" in out
    out = cli.run(["look sou"])
    assert "can't look that way" in out.lower()


def test_look_item_and_monster(cli, world):
    world.place_item(2000, 0, 0, "gold_chunk")
    out = cli.run(["look gold"])
    assert "gold-chunk" in out.lower()
    world.place_monster(2000, 1, 0, "mutant")
    out = cli.run(["look mut"])
    assert "can't look that way" in out.lower()


def test_footsteps_only_on_move(cli, world):
    out1 = cli.run(["look"])
    assert "footsteps" not in out1.lower()
    out2 = cli.run(["n"])
    assert "footsteps" not in out2.lower()
    world.force_monster_move_within4()
    out3 = cli.run(["n"])
    assert "footsteps nearby" in out3.lower()
