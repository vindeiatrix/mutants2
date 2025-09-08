from mutants2.engine import world as world_mod, persistence, loop
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context

import contextlib
import tempfile
import re
from pathlib import Path
import io


def run_commands(cmds, setup=None):
    save = persistence.Save()
    w = world_mod.World()
    w.year(2000)
    p = Player(year=2000, clazz="Warrior")
    if setup:
        setup(w, p)
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            for c in cmds:
                ctx.dispatch_line(c)
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    buf.close()
    return out, w, p, ctx


def test_select_target_triggers_tick():
    def setup(w, p):
        w.place_monster(2000, 0, 0, "mutant")
        w.place_monster(2000, 1, 0, "mutant")
        w.monster_here(2000, 1, 0)["aggro"] = True

    out, w, p, _ = run_commands(["com muta"], setup=setup)
    assert re.search(r"You're ready to combat Mutant-\d{4}!", out)
    assert "has just arrived from the east." in out
    assert w.turn == 1


def test_help_paths():
    out, w, _p, _ = run_commands(["combat"])
    assert "ready yourself for battle" in out
    assert w.turn == 0
    out2, w2, _p2, _ = run_commands(["help combat"])
    assert "ready yourself for battle" in out2
    assert w2.turn == 0


def test_target_cleared_on_player_death():
    def setup(w, p):
        w.place_monster(2000, 0, 0, "mutant")

    out, w, p, ctx = run_commands(["combat mutant"], setup=setup)
    assert p.ready_to_combat_name is not None
    p.hp = 1
    p.ions = 0
    with contextlib.redirect_stdout(io.StringIO()):
        loop.process_upkeep_and_starvation(p, w, persistence.Save())
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("status")
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    assert "Ready to Combat: NO ONE" in out


def test_target_cleared_on_monster_death():
    def setup(w, p):
        w.place_monster(2000, 0, 0, "mutant")

    out, w, p, ctx = run_commands(["combat mutant"], setup=setup)
    assert p.ready_to_combat_name is not None
    w.damage_monster(2000, 0, 0, 99, player=p)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("status")
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    assert "Ready to Combat: NO ONE" in out
