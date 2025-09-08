import io
import re
import contextlib
import tempfile
from pathlib import Path

from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context


def run_commands(cmds, setup=None):
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
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    buf.close()
    return out, w, p


def test_get_suppresses_room_render():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, {"key": "skull"})

    out, _, _ = run_commands(["get skull"], setup=setup)
    assert "You pick up A Skull." in out
    assert "You are here." not in out
    assert "Compass:" not in out


def test_inventory_hides_worn_armor():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, {"key": "bug-skin"})

    out, _, _ = run_commands(
        ["get bug", "wear bug", "inventory", "remove", "inventory"], setup=setup
    )
    blocks = out.split("You are carrying the following items:")
    first = blocks[1].split("remove", 1)[0]
    second = blocks[2]
    assert "Bug-Skin" not in first
    assert "Bug-Skin" in second


def test_wield_without_target_suppresses_line():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, {"key": "light_spear"})

    out, _, _ = run_commands(["get light", "wield light"], setup=setup)
    assert "You wield the Light-Spear." not in out
    assert "You're not ready to combat anyone." in out


def test_kill_rewards():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, {"key": "light_spear"})
        w.place_monster(2000, 0, 0, "mutant")

    out, _, p = run_commands(
        ["get light", "combat mutant", "wield light", "status"], setup=setup
    )
    assert "You collect 20000 Riblets and 20000 ions from the slain body." in out
    assert re.search(r"A Skull is falling from Mutant-\d{4}'s body!", out)
    assert re.search(r"\*\*\*\nMutant-\d{4} is crumbling to dust!", out)
    assert "You gain" not in out
    assert p.riblets == 20000 and p.ions == 20000


def test_convert_bug_skin_plus_one_and_look():
    def setup(w, p):
        p.inventory.append({"key": "bug-skin", "enchant": 1})

    out, _, p = run_commands(["look bug", "convert bug", "status"], setup=setup)
    assert "possesses a magical aura" in out
    assert "+1 Bug-Skin" in out
    assert "You convert the Bug-Skin into 22100 ions." in out
    assert p.ions == 22100
