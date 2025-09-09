import contextlib
import io
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
    return buf.getvalue()


def test_inventory_vs_worn():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "bug-skin")

    out = run(["get bug", "wear bug", "inventory"], setup)
    assert "You wear the Bug-Skin." in out
    assert "Bug-Skin" not in out.split("inventory")[-1]
