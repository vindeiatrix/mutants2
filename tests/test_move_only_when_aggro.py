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
def world_cross_year(seeded_rng):
    w = world_mod.World()
    w.year(2000)
    w.place_monster(2000, 0, 2, "mutant")  # passive in current year
    w.year(2100)
    w.place_monster(2100, 0, 1, "mutant")
    w.monster_here(2100, 0, 1)["aggro"] = True
    return w


@pytest.fixture
def cli(world_cross_year, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player()
    p.clazz = "Warrior"
    ctx = make_context(p, world_cross_year, save)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


def test_tick_skipped_when_no_aggro(cli, world_cross_year):
    before = list(world_cross_year.monster_positions(2100))[0][:2]
    out = cli.run(["look"])
    after = list(world_cross_year.monster_positions(2100))[0][:2]
    assert before == after
    assert "footsteps" not in out.lower()
