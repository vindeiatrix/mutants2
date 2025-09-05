import contextlib
import io

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


def test_inventory_render_only(tmp_path):
    persistence.SAVE_PATH = tmp_path / 'save.json'
    w = world_mod.World(seeded_years={2000})
    p = Player(year=2000, clazz='Warrior')
    p.inventory.append('ion_decay')
    save = persistence.Save()
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line('inventory')
    out = buf.getvalue()
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert 'You are carrying the following items:' in lines[1]
    assert 'Ion-Decay' in lines[2]
    assert all('Compass' not in ln for ln in lines)
    assert w.turn == 0
