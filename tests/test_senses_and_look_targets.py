import contextlib
from io import StringIO

import pytest

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.ui.theme import yellow


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
    assert "shadows to the east" in out.lower()


def test_look_dir_and_blocked(cli):
    out = cli.run(["loo n"])
    assert "***" in out
    out = cli.run(["look sou"])
    assert "***" in out


def test_look_item_and_monster(cli, world):
    world.place_item(2000, 0, 0, "gold_chunk")
    out = cli.run(["look gold"])
    assert yellow("You can't see Gold-Chunk.") in out
    world.place_monster(2000, 1, 0, "mutant")
    out = cli.run(["look mut"])
    assert yellow("You can't see Mut.") in out
