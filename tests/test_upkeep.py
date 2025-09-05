import io
import contextlib
import re

from mutants2.engine import loop, world as world_mod, persistence
from mutants2.engine.player import Player


def run_upkeep(p, *, now, save=None):
    w = world_mod.World(global_seed=42)
    if save is None:
        save = persistence.Save(global_seed=42, last_upkeep_tick=0)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        loop.ion_upkeep(p, w, save, now=now)
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    return out, p, save


def test_additive_upkeep_examples():
    p = Player(year=2000, clazz="Thief", level=2, ions=1000, hp=20, max_hp=20)
    out, p, save = run_upkeep(p, now=10)
    assert p.ions == 750
    assert save.last_upkeep_tick == 10
    p2 = Player(year=2000, clazz="Mage", level=12, ions=1000, hp=20, max_hp=20)
    out2, p2, save2 = run_upkeep(p2, now=10)
    assert p2.ions == 0
    assert "You're starving for IONS!" in out2
    assert save2.last_upkeep_tick == 10


def test_starvation_tick_cadence():
    p = Player(year=2000, clazz="Warrior", level=5, ions=0, hp=20, max_hp=20)
    save = persistence.Save(global_seed=42, last_upkeep_tick=0)
    out1, p, save = run_upkeep(p, now=10, save=save)
    assert "You're starving for IONS!" in out1
    assert p.hp == 15
    out2, p, save = run_upkeep(p, now=15, save=save)
    assert "You're starving for IONS!" not in out2
    assert p.hp == 15
    out3, p, save = run_upkeep(p, now=20, save=save)
    assert "You're starving for IONS!" in out3
    assert p.hp == 10


def test_starvation_death_stops():
    p = Player(year=2000, clazz="Warrior", level=5, ions=0, hp=5, max_hp=5)
    save = persistence.Save(global_seed=42, last_upkeep_tick=0)
    out, p, save = run_upkeep(p, now=25, save=save)
    assert "You have died." in out
    assert p.hp == p.max_hp
    assert save.last_upkeep_tick == 10
