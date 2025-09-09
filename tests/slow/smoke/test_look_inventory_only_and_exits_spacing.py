import contextlib
import datetime
import io

from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.ui.theme import COLOR_HEADER, COLOR_ITEM


def _ctx(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"
    w = world_mod.World({(2000, 0, 0): ["nuclear_rock"]}, {2000})
    p = Player(year=2000, clazz="Warrior")
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    ctx = make_context(p, w, save)
    return ctx, w


def test_look_inventory_only(tmp_path):
    ctx, w = _ctx(tmp_path)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("look nuclear")
    out = buf.getvalue()
    assert COLOR_HEADER("You can't see nuclear.") in out
    assert "You are here." not in out
    assert "Compass:" not in out
    assert w.turn == 1
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("get nuclear-rock")
        ctx.dispatch_line("look nuclear")
    out = buf.getvalue()
    assert COLOR_HEADER("It looks like a lovely Nuclear-Rock!") in out
    assert "You are here." not in out
    assert "Compass:" not in out
    assert w.turn == 3


def test_exit_spacing(tmp_path):
    ctx, _ = _ctx(tmp_path)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("look")
    out = buf.getvalue()
    north_line = f"{COLOR_HEADER('north')} – {COLOR_ITEM('area continues.')}"
    south_line = f"{COLOR_HEADER('south')} – {COLOR_ITEM('area continues.')}"
    east_line = f"{COLOR_HEADER('east')}  – {COLOR_ITEM('area continues.')}"
    west_line = f"{COLOR_HEADER('west')}  – {COLOR_ITEM('area continues.')}"
    assert north_line in out
    assert south_line in out
    assert east_line in out
    assert west_line in out
    assert "\x1b[34m" not in out
