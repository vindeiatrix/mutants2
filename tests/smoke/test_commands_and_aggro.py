from __future__ import annotations

import contextlib
import io
import re
import tempfile
from pathlib import Path

from mutants2.cli.shell import make_context, resolve_command
from mutants2.engine import world as world_mod, persistence
from mutants2.engine.player import Player
from mutants2.testing_api import run_one


def run_commands(cmds, *, seed: int = 42, setup=None):
    save = persistence.Save(global_seed=seed)
    w = world_mod.World(global_seed=seed)
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


def test_x_alias_and_help():
    assert resolve_command("x") == "class"
    out = run_one("help")
    assert "class (or x)" in out


def test_blank_enter_hint():
    out, w, _p, _ctx = run_commands([""])
    lines = out.strip().splitlines()
    assert lines == ["***", "Type ? if you need assistance."]
    assert w.turn == 0


def test_look_reroll_yells_once():
    def setup(w, p):
        w.place_monster(2000, 0, 0, "mutant")

    out, _w, _p, _ = run_commands(["look", "look"], seed=0, setup=setup)
    assert out.splitlines().count("Mutant yells at you!") <= 1


def test_arrival_separators():
    def setup(w, p):
        w.place_monster(2000, 1, 0, "mutant")
        w.monster_here(2000, 1, 0)["aggro"] = True
        w.place_monster(2000, -1, 0, "mutant")
        w.monster_here(2000, -1, 0)["aggro"] = True

    out, _w, _p, _ = run_commands(["look"], setup=setup)
    assert out.count("has just arrived") == 2
    first = out.find("has just arrived")
    second = out.find("has just arrived", first + 1)
    between = out[first:second]
    assert "***" in between


def test_exit_resets_aggro():
    def setup(w, p):
        w.place_monster(2000, 1, 0, "mutant")
        w.monster_here(2000, 1, 0)["aggro"] = True

    out, w, _p, _ = run_commands(["look", "exit"], setup=setup)
    assert "Goodbye." in out
    assert not w.any_aggro_in_year(2000)
