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
    for x, y, _ in list(w.monster_positions(2000)):
        w.remove_monster(2000, x, y)
    w.place_monster(2000, 0, 0, "mutant")
    w.monster_here(2000, 0, 0)["aggro"] = True
    w.place_monster(2000, 1, 0, "mutant")
    return w


@pytest.fixture
def cli(world, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player()
    p.clazz = "Warrior"
    ctx = make_context(p, world, save)

    def always_aggro(year, x, y, player, seed_parts=()):
        yells = []
        for m in world.monsters_here(year, x, y):
            if not m.get("aggro"):
                m["aggro"] = True
                yells.append(f"{m['name']} yells at you!")
        return yells

    monkeypatch.setattr(world, "on_entry_aggro_check", always_aggro)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


def test_resident_yell_precedes_arrival(cli):
    out = cli.run(["e"])
    y_idx = out.find("yells at you")
    a_idx = out.find("has just arrived")
    assert y_idx != -1 and a_idx != -1 and y_idx < a_idx
