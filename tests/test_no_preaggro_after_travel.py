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
def world_travel_passive(seeded_rng):
    w = world_mod.World()
    w.year(2200)
    w.place_monster(2200, 0, 2, "mutant")
    return w


@pytest.fixture
def cli(world_travel_passive, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player()
    p.clazz = "Warrior"
    ctx = make_context(p, world_travel_passive, save)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


def test_no_preaggro_after_travel(cli):
    out = cli.run(["travel 2200"])
    text = out.lower()
    assert "footsteps" not in text
    assert "has just arrived" not in text
    out2 = cli.run(["look"])
    text2 = out2.lower()
    assert "footsteps" not in text2
    assert "has just arrived" not in text2
