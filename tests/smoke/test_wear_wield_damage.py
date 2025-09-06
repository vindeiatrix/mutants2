import contextlib
import tempfile
import re
import io
from pathlib import Path

from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.engine import items


BASE_POWERS = {
    "monster_bait": 2,
    "cigarette_butt": 3,
    "light_spear": 3,
    "skull": 4,
    "cheese": 4,
    "nuclear_thong": 5,
    "ion_booster": 5,
    "nuclear_rock": 7,
    "nuclear_waste": 7,
    "ion_decay": 10,
    "ion_pack": 12,
    "bottle_cap": 14,
    "gold_chunk": 17,
    "nuclear_decay": 77,
}


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


def test_base_powers_and_armor():
    for key, power in BASE_POWERS.items():
        assert items.REGISTRY[key].base_power == power
    assert items.REGISTRY["bug_skin_armour"].ac_bonus == 3


def test_wear_and_remove_updates_ac():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "bug_skin_armour")
    out, w, p = run_commands([
        "get bug",
        "wear bug",
        "status",
        "remove",
        "status",
    ], setup=setup)
    assert "You wear the Bug-Skin-Armour." in out
    assert "You remove the Bug-Skin-Armour." in out
    matches = re.findall(r"Wearing Armor: .*  Armour Class: (\d+)", out)
    assert len(matches) == 2 and int(matches[0]) == int(matches[1]) + 3


def test_wield_attack_damage():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "nuclear_rock")
        w.place_monster(2000, 0, 0, "mutant")
    out, w, p = run_commands([
        "get nuc",
        "combat mutant",
        "wield nuc",
        "status",
    ], setup=setup)
    assert "You wield the Nuclear-Rock." in out
    expected = items.REGISTRY["nuclear_rock"].base_power + p.strength // 10
    pattern = rf"You hit Mutant-\d{{4}} for {expected} damage\.  \(temp\)"
    assert re.search(pattern, out)
    assert "Ready to Combat: NO ONE" in out
    assert w.monster_here(2000, 0, 0) is None
