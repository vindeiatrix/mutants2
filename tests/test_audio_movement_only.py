import contextlib
from io import StringIO

import pytest

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


@pytest.fixture
def seeded_rng(monkeypatch):
    import hashlib
    import random
    from mutants2.engine import rng

    def fake_hrand(*parts):
        h = hashlib.md5(str(parts).encode()).hexdigest()
        seed = int(h, 16) & 0xFFFFFFFF
        return random.Random(seed)

    monkeypatch.setattr(rng, "hrand", fake_hrand)


@pytest.fixture
def world_passive_monster_south(seeded_rng):
    w = world_mod.World()
    w.year(2000)
    w.place_monster(2000, 0, 2, "mutant")
    return w


@pytest.fixture
def world_passive_monster_here_after_move(seeded_rng):
    w = world_mod.World()
    w.year(2000)
    w.place_monster(2000, 0, 1, "mutant")
    # Extra aggro monster that can move toward the player on subsequent turns
    w.place_monster(2000, 2, 1, "mutant")
    w.monster_here(2000, 2, 1)["aggro"] = True
    return w


@pytest.fixture
def world_aggro_monster_two_south(seeded_rng):
    w = world_mod.World()
    w.year(2000)
    w.place_monster(2000, 0, 3, "mutant")
    w.monster_here(2000, 0, 3)["aggro"] = True
    return w


@pytest.fixture
def cli(tmp_path, monkeypatch, request):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player()
    p.clazz = "Warrior"
    world = None
    for name in (
        "world_passive_monster_south",
        "world_passive_monster_here_after_move",
        "world_aggro_monster_two_south",
    ):
        if name in request.fixturenames:
            world = request.getfixturevalue(name)
            break
    if world is None:
        world = world_mod.World()
        world.year(2000)
    ctx = make_context(p, world, save)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


def test_no_footsteps_before_aggro(cli, world_passive_monster_south):
    out1 = cli.run(["look"])
    out2 = cli.run(["look"])
    out3 = cli.run(["look"])
    assert "footsteps" not in (out1 + out2 + out3).lower()


def test_yell_once_on_entry_then_move(cli, world_passive_monster_here_after_move):
    out = cli.run(["n"])
    if "yells at you" in out.lower():
        out2 = cli.run(["look"])
        assert "footsteps" in out2.lower() or "has just arrived" in out2.lower()
        out3 = cli.run(["look"])
        assert "yells at you" not in out3.lower()


def test_footsteps_only_when_moved(cli, world_aggro_monster_two_south):
    out = cli.run(["look"])
    text = out.lower()
    assert "faint" in text and "footsteps" in text and "south" in text
