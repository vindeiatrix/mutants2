import contextlib
import io
import datetime

from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.ui.theme import yellow


def _ctx(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"
    w = world_mod.World({(2000, 0, 0): [{"key": "bug-skin", "enchant": 0}]}, {2000})
    p = Player(year=2000, clazz="Warrior")
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    ctx = make_context(p, w, save)
    return ctx


def test_look_inventory_only(tmp_path):
    ctx = _ctx(tmp_path)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("look bug")
    out = buf.getvalue()
    assert yellow("You can't see bug.") in out
    assert "Compass:" not in out

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("get bug")
        ctx.dispatch_line("look bug")
    out = buf.getvalue()
    assert yellow("It looks like a lovely Bug-Skin!") in out
    assert "Compass:" not in out
