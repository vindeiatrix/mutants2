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
    for (x, y), _ in list(w.monsters_in_year(2000).items()):
        w.remove_monster(2000, x, y)
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
def world_with_aggro_south(world):
    world.place_monster(2000, 4, 0, "mutant")
    world.monster_here(2000, 4, 0)["aggro"] = True
    return world


@pytest.fixture
def staged_world_far_south(world):
    world.place_monster(2000, 4, 0, "mutant")
    world.monster_here(2000, 4, 0)["aggro"] = True
    return world


@pytest.fixture
def staged_world_adjacent_south(world):
    world.place_monster(2000, 1, 0, "mutant")
    world.monster_here(2000, 1, 0)["aggro"] = True
    return world


@pytest.fixture
def world_two_adjacent(world):
    world.place_monster(2000, 1, 0, "mutant")
    world.place_monster(2000, 0, -1, "mutant")
    return world


def test_look_consumes_turn(cli, world_with_aggro_south):
    out = cli.run(["look"])
    assert "You hear" in out or "You see shadows" in out


def test_faint_then_loud_then_shadows_progression(cli, staged_world_far_south):
    out1 = cli.run(["loo"])
    assert "faint" in out1 and "east" in out1
    outL = None
    for _ in range(5):
        out = cli.run(["loo"])
        if "loud" in out and "footsteps" in out:
            outL = out
            break
    assert outL and "east" in outL
    outS = None
    for _ in range(5):
        out = cli.run(["loo"])
        if "You see shadows to the east" in out:
            outS = out
            break
    assert outS


def test_arrival_message(cli, staged_world_adjacent_south):
    out = cli.run(["loo"])
    assert "has just arrived from the east" in out
    # Presence should be suppressed on the same tick as the arrival
    assert "is here" not in out.split("has just arrived")[-1]


def test_multi_shadow(cli, world_two_adjacent):
    out = cli.run(["look"])
    assert "shadows to the east, south" in out or "south, east" in out
