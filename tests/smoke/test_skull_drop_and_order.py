import contextlib
import io
import re
import tempfile
from pathlib import Path

from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.ui.theme import red, SEP


def run_commands(cmds, setup=None):
    save = persistence.Save()
    w = World()
    w.year(2000)
    p = Player(year=2000, clazz="Warrior")
    if setup:
        setup(w, p)
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    orig = persistence.SAVE_PATH
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            for c in cmds:
                ctx.dispatch_line(c)
    persistence.SAVE_PATH = orig
    return buf.getvalue()


def test_skull_drop_and_order():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, {"key": "light_spear"})
        w.place_monster(2000, 0, 0, "mutant")

    out = run_commands(
        ["get light", "combat mutant", "wield light", "get skull", "inventory"],
        setup=setup,
    )

    collect = red("You collect 20000 Riblets and 20000 ions from the slain body.")
    assert collect in out
    drop_match = re.search(
        r"\x1b\[37mA Skull is falling from Mutant-\d{4}'s body!\x1b\[0m",
        out,
    )
    assert drop_match
    assert out.find(collect) < drop_match.start()
    crumble_match = re.search(
        rf"{re.escape(SEP)}\n\x1b\[31mMutant-\d{{4}} is crumbling to dust!\x1b\[0m",
        out,
    )
    assert crumble_match
    assert drop_match.end() < crumble_match.start()
    assert "You pick up A Skull." in out
    assert "Skull." in out
