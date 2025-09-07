import contextlib
from io import StringIO

import pytest

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


previous_baseline_monsters = 54
previous_baseline_items = 45


@pytest.fixture
def world():
    w = world_mod.World()
    w.year(2000)
    for x, y, _ in list(w.monster_positions(2000)):
        w.remove_monster(2000, x, y)
    w.ground.clear()
    return w


@pytest.fixture
def player():
    p = Player()
    p.clazz = "Warrior"
    return p


def _make_cli(world, player, tmp_path, monkeypatch):
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

        @property
        def world(self):
            return world

        @property
        def player(self):
            return player

    return CLI()


@pytest.fixture
def cli(world, player, tmp_path, monkeypatch):
    return _make_cli(world, player, tmp_path, monkeypatch)


@pytest.fixture
def world_with_adjacent_monster(world):
    world.place_monster(2000, 0, 2, "mutant")
    return world


@pytest.fixture
def world_with_two_monsters_here(world):
    world.place_monster(2000, 0, 0, "mutant")
    world.place_monster(2000, 0, 0, "mutant")
    return world


@pytest.fixture
def staged_arrival_now_into_room_with_another_monster(world):
    world.place_monster(2000, 0, 0, "mutant")
    world.place_monster(2000, 1, 0, "mutant")
    world.monster_here(2000, 1, 0)["aggro"] = True
    return world


@pytest.fixture
def seeded_world():
    w = world_mod.World(seed_monsters=True)
    w.year(2000)
    return w


@pytest.fixture
def cli_seeded(seeded_world, player, tmp_path, monkeypatch):
    return _make_cli(seeded_world, player, tmp_path, monkeypatch)


def test_peek_has_no_shadows(cli, world_with_adjacent_monster):
    out = cli.run(["look so"])
    assert "You see shadows" not in out


def test_single_echo(cli):
    out = cli.run(["inv"])
    assert out.splitlines().count("inv") == 1
    assert "> inv" not in out


def test_multi_monster_presence_line(cli, world_with_two_monsters_here):
    out = cli.run(["look"])
    assert "are here with you." in out and "," in out and "and" in out


def test_arrival_suppresses_presence(cli, staged_arrival_now_into_room_with_another_monster):
    out = cli.run(["look"])
    assert "has just arrived" in out
    assert "is here with you" not in out and "is here." not in out.split("has just arrived")[-1]


def test_spawn_scaling(cli_seeded):
    m_count = cli_seeded.world.count_monsters_for_year(cli_seeded.player.year)
    i_count = cli_seeded.world.count_items_for_year(cli_seeded.player.year)
    assert m_count >= previous_baseline_monsters * 0.5 * 0.8
    assert i_count >= previous_baseline_items * 10 * 0.8
