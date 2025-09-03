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
def player():
    p = Player()
    p.clazz = "Warrior"
    return p


@pytest.fixture
def cli(world, player, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    ctx = make_context(player, world, save)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


@pytest.fixture
def world_with_items(world):
    world.place_item(2000, 0, 0, "nuclear_thong")
    world.place_item(2000, 0, 0, "nuclear_rock")
    return world


@pytest.fixture
def world_with_monster_and_item_N_on_tile(world, player):
    world.place_monster(2000, 0, 0, "night_stalker")
    player.inventory["nuclear_thong"] = 1
    return world


def test_command_prefix_3_to_full(cli):
    assert "***" in cli.run(["tra 2100"])
    assert "***" in cli.run(["trav 2100"])
    assert "***" in cli.run(["trave 2100"])
    assert "***" in cli.run(["travel 2100"])
    assert "Unknown command" in cli.run(["tr 2100"])


def test_directions_special(cli):
    assert "***" in cli.run(["n"])
    assert "***" in cli.run(["north"])
    assert "Unknown command" in cli.run(["nor"])


def test_item_prefix_first_match(cli, world_with_items):
    out = cli.run(["get n"])
    assert "You pick up Nuclear-thong." in out
    out2 = cli.run(["dro nuc"])
    assert "You drop Nuclear-thong." in out2


def test_look_monster_precedence(cli, world_with_monster_and_item_N_on_tile):
    out = cli.run(["loo n"])
    assert "It's a Night-Stalker." in out

def test_look_direction_fallback(cli):
    out = cli.run(["loo e"])
    assert "can't look that way" not in out.lower()
