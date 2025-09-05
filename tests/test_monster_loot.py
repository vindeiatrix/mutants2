import contextlib
import io
import re

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_kill_loot_award(tmp_path):
    persistence.SAVE_PATH = tmp_path / 'save.json'
    w = world_mod.World(
        monsters={(2000, 0, 0): [{"key": "mutant", "hp": 3, "loot_ions": 5, "loot_riblets": 7}]},
        seeded_years={2000},
    )
    p = Player(year=2000, clazz='Warrior')
    save = persistence.Save()
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line('attack')
        ctx.dispatch_line('attack')
    out = strip_ansi(buf.getvalue())
    assert 'You have slain Mutant-' in out
    assert 'Your experience points are increased by 20,000!' in out
    assert 'You collect 20,007 Riblets and 20,005 ions' in out
    assert p.ions == 20005
    assert p.riblets == 20007


def test_death_transfer_and_reward(tmp_path):
    persistence.SAVE_PATH = tmp_path / 'save.json'
    w = world_mod.World(
        monsters={(2000, 0, 0): [{"key": "leucrotta", "hp": 3}]}, seeded_years={2000}
    )
    p = Player(year=2000, clazz='Warrior', hp=1, max_hp=1, ions=12345, riblets=67890)
    save = persistence.Save()
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line('attack')
    m = w.monster_here(2000, 0, 0)
    assert p.ions == 0
    assert p.riblets == 0
    assert int(m.get('loot_ions')) == 12345
    assert int(m.get('loot_riblets')) == 67890
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line('attack')
    assert p.ions == 20000 + 12345
    assert p.riblets == 20000 + 67890
