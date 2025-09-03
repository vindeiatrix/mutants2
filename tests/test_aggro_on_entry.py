from io import StringIO
import contextlib

import pytest

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


@pytest.fixture
def world_with_passive_mutant_here(seeded_rng):
    w = world_mod.World()
    w.year(2000)
    for x, y, _ in list(w.monster_positions(2000)):
        w.remove_monster(2000, x, y)
    w.place_monster(2000, 0, 0, "mutant")  # passive by default
    return w


@pytest.fixture
def cli(world_with_passive_mutant_here, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player()
    p.clazz = "Warrior"
    ctx = make_context(p, world_with_passive_mutant_here, save)

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
    import hashlib
    import random
    from mutants2.engine import rng

    def fake_hrand(*parts):
        h = hashlib.md5(str(parts).encode()).hexdigest()
        seed = int(h, 16) & 0xFFFFFFFF
        return random.Random(seed)

    monkeypatch.setattr(rng, "hrand", fake_hrand)


def test_on_entry_rolls(cli, world_with_passive_mutant_here, seeded_rng):
    out = cli.run(["look"])
    assert "yells at you" not in out.lower()
    out2 = cli.run(["n", "s"])
    assert "yells at you" in out2.lower()
