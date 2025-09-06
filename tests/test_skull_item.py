import contextlib
import io
import re
import contextlib

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.types import ItemInstance


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_skull_look_and_convert(tmp_path):
    persistence.SAVE_PATH = tmp_path / 'save.json'
    w = world_mod.World(seeded_years={2000})
    p = Player(year=2000, clazz='Warrior')
    p.inventory.append({"key": "skull", "meta": {"monster_type": "Crio-Sphinx"}})
    save = persistence.Save()
    ctx = make_context(p, w, save)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line('look skull')
    out = strip_ansi(buf.getvalue())
    assert 'of a Crio-Sphinx!' in out

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line('convert skull')
        ctx.dispatch_line('inventory')
        ctx.dispatch_line('status')
    out = strip_ansi(buf.getvalue())
    assert 'You convert the Skull into 25000 ions.' in out
    assert '(empty)' in out
    assert 'Ions         : 25000' in out
