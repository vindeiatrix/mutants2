import contextlib
import datetime
import io

from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.ui.theme import yellow


def run_world(w):
    p = Player(year=2000, clazz="Warrior")
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("look")
    return buf.getvalue().lower()


def blank_world(monsters):
    w = world_mod.World()
    w.year(2000)
    for (x, y), _ in list(w.monsters_in_year(2000).items()):
        w.remove_monster(2000, x, y)
    for x, y in monsters:
        w.place_monster(2000, x, y, "mutant")
        w.monster_here(2000, x, y)["aggro"] = True
    return w


def test_diagonal_and_cardinal_footsteps(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"

    w = blank_world([(-2, -2)])
    out = run_world(w)
    assert "south-west" in out

    w = blank_world([(2, 0)])
    out = run_world(w)
    assert "east" in out

    w = blank_world([(-1, 1)])
    out = run_world(w)
    assert "footsteps" not in out


def test_spawnable_look_lovely(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"
    w = world_mod.World({(2000, 0, 0): ["nuclear_rock"]}, {2000})
    p = Player(year=2000, clazz="Warrior")
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("look nuclear")
    out = buf.getvalue()
    assert yellow("You can't see Nuclear-Rock.") in out
