import contextlib
import io
import re
import tempfile
from pathlib import Path

from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context


def run(cmds, setup=None):
    save = persistence.Save()
    w = World()
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
    return re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())


def test_kill_loot_pipeline():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "nuclear_rock")
        w.place_monster(2000, 0, 0, "mutant")

    out = run(
        [
            "get nuclear-rock",
            "combat mutant",
            "wield nuclear-rock",
            "get skull",
        ],
        setup,
    )
    assert "You collect 20000 Riblets and 20000 ions" in out
    assert "You pick up A Skull." in out
