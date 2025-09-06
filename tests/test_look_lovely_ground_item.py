import contextlib
import datetime
import io

from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.ui.theme import yellow


def test_look_ground_item_not_carried(tmp_path):
    persistence.SAVE_PATH = tmp_path / 'save.json'
    w = world_mod.World({(2000, 0, 0): ['nuclear_rock']}, {2000})
    p = Player(year=2000, clazz='Warrior')
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line('look nuclear')
    out = buf.getvalue()
    assert yellow('It looks like a lovely Nuclear-Rock!') in out
