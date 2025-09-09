import contextlib
import datetime
import io

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


def test_room_render_gating(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"
    w = world_mod.World({(2000, 0, 0): ["bug_skin", "ion_decay"]}, {2000})
    w.place_monster(2000, 0, 0, "mutant")
    p = Player(year=2000, clazz="Warrior", hp=5, max_hp=10, ions=50000)
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    ctx = make_context(p, w, save, dev=True)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("look")
        ctx.dispatch_line("get bug")
        ctx.dispatch_line("wear bug")
        ctx.dispatch_line("get ion")
        ctx.dispatch_line("wield ion")
        ctx.dispatch_line("convert ion")
        ctx.dispatch_line("heal")
        ctx.dispatch_line("combat mutant")
        ctx.dispatch_line("debug shadow north")
        ctx.dispatch_line("east")
        ctx.dispatch_line("look")
    out = buf.getvalue()
    assert out.count("Compass:") == 3
