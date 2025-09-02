from io import StringIO
import contextlib

import pytest

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


@pytest.fixture
def world_with_passive_here(seeded_rng):
    w = world_mod.World()
    w.year(2000)
    w.place_monster(2000, 0, 0, "mutant")  # passive by default
    return w


@pytest.fixture
def cli(world_with_passive_here, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player()
    p.clazz = "Warrior"
    ctx = make_context(p, world_with_passive_here, save)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


@pytest.fixture
def seeded_rng(monkeypatch):
    import hashlib, random
    from mutants2.engine import rng, monsters as monsters_mod

    def fake_hrand(*parts):
        h = hashlib.md5(str(parts).encode()).hexdigest()
        seed = int(h, 16) & 0xFFFFFFFF
        return random.Random(seed)

    monkeypatch.setattr(rng, "hrand", fake_hrand)
    monsters_mod._next_id = 1


def test_passive_monsters_do_not_move(cli, seeded_rng):
    out = cli.run(["look"])  # passive, no movement
    assert "has just arrived" not in out.lower()
    out2 = cli.run(["n", "s"])  # re-enter to trigger aggro
    assert "yells at you" in out2.lower()
    out3 = cli.run(["n"])  # move away so aggro monster chases
    assert "has just arrived" in out3.lower()

