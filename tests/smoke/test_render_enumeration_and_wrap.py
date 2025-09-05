import contextlib
import datetime
import io

from mutants2.engine import persistence, world as world_mod, items
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.ui.theme import yellow, white, cyan


def _ctx(tmp_path):
    persistence.SAVE_PATH = tmp_path / 'save.json'
    w = world_mod.World(seeded_years={2000})
    p = Player(year=2000, clazz='Warrior')
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    ctx = make_context(p, w, save, dev=True)
    return ctx


def test_enumeration_and_wrap(tmp_path):
    ctx = _ctx(tmp_path)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line('debug item add cheese 2')
        ctx.dispatch_line('look')
    out = buf.getvalue()
    assert yellow('On the ground lies:') in out
    assert cyan('A Cheese, A Cheese (1).') in out

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line('get cheese')
        ctx.dispatch_line('get cheese')
        ctx.dispatch_line('debug item add nuclear_rock')
        ctx.dispatch_line('get nuclear-rock')
        ctx.dispatch_line('debug item add cheese')
        ctx.dispatch_line('get cheese')
        ctx.dispatch_line('inventory')
    inv_out = buf.getvalue()
    assert white('Cheese, Cheese (1), Nuclear-Rock, Cheese (2).') in inv_out

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        for _ in range(5):
            ctx.dispatch_line('debug item add nuclear_rock')
            ctx.dispatch_line('get nuclear-rock')
        for _ in range(5):
            ctx.dispatch_line('debug item add ion_decay')
            ctx.dispatch_line('get ion-decay')
        ctx.dispatch_line('inventory')
    wrap_out = buf.getvalue()
    item_lines = [
        ln for ln in wrap_out.splitlines() if 'Cheese' in ln or 'Nuclear-Rock' in ln or 'Ion-Decay' in ln
    ]
    assert len(item_lines) >= 2
    assert 'Nuclear-\nRock' not in wrap_out
