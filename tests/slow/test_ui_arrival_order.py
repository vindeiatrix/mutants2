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
def staged_adjacent_then_arrival(world):
    # Adjacent east monster for immediate arrival when staying put
    world.place_monster(2000, 1, 0, "mutant")
    world.monster_here(2000, 1, 0)["aggro"] = True
    # Monster two tiles north that will arrive after the player moves north
    world.place_monster(2000, 0, 2, "mutant")
    world.monster_here(2000, 0, 2)["aggro"] = True
    return world


@pytest.fixture
def staged_arrival_now(world):
    world.place_monster(2000, 1, 0, "mutant")
    world.monster_here(2000, 1, 0)["aggro"] = True
    return world


def test_shadows_then_arrival(cli, staged_adjacent_then_arrival):
    out = cli.run(["n"])
    s_idx = out.find("You see shadows")
    a_idx = out.find("has just arrived")
    assert s_idx != -1 and a_idx != -1 and s_idx < a_idx


def test_no_presence_on_arrival_tick(cli, staged_arrival_now):
    out = cli.run(["look"])
    assert "has just arrived" in out
    assert "is here." not in out.split("has just arrived")[-1]


def test_arrival_colored_red(cli, staged_arrival_now):
    out = cli.run(["look"])
    assert "\x1b[31m" in out and "\x1b[0m" in out


def test_prompt_echo_without_arrow(cli):
    out = cli.run(["w"])
    assert "\n> w" not in out
    assert out.startswith("w\n")


def test_single_separator_between_events(cli, staged_adjacent_then_arrival):
    out = cli.run(["look"])
    chunk = out.split("You see shadows")[1]
    assert chunk.count("***") >= 1
    # guard against duplicate separators around the arrival block
    assert "***\n***" not in chunk
