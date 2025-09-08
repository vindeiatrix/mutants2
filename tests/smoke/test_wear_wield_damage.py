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
from mutants2.engine.items_util import coerce_item


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
    assert items.REGISTRY["bug-skin"].ac_bonus == 3


def test_wear_and_remove_updates_ac():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "bug-skin")

    out, w, p = run_commands(
        [
            "get bug",
            "wear bug",
            "status",
            "remove",
            "status",
        ],
        setup=setup,
    )
    assert "You wear the Bug-Skin." in out
    assert "You remove the Bug-Skin." in out
    matches = re.findall(r"Wearing Armor: .*  Armour Class: (\d+)", out)
    assert len(matches) == 2 and int(matches[0]) == int(matches[1]) + 3


def test_wield_attack_damage():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "nuclear_rock")
        w.place_monster(2000, 0, 0, "mutant")

    out, w, p = run_commands(
        [
            "get nuclear-rock",
            "combat mutant",
            "wield nuc",
            "status",
        ],
        setup=setup,
    )
    assert "You wield the Nuclear-Rock." in out
    expected = items.REGISTRY["nuclear_rock"].base_power + p.strength // 10
    pattern = rf"You hit Mutant-\d{{4}} for {expected} damage\.  \(temp\)"
    assert re.search(pattern, out)
    assert "Ready to Combat: NO ONE" in out
    assert w.monster_here(2000, 0, 0) is None


def test_cannot_wield_worn_item():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "bug-skin")

    out, _, _ = run_commands(["get bug", "wear bug", "wield bug"], setup=setup)
    assert "You're not carrying a Bug-Skin." in out
    assert "You cannot wield" not in out
    assert "You're not ready to combat anyone." not in out


def test_wield_prefers_inventory_copy():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "bug-skin")
        w.add_ground_item(2000, 0, 0, "bug-skin")
        w.place_monster(2000, 0, 0, "mutant")

    out, w, p = run_commands(
        ["get bug", "get bug", "wear bug", "combat mutant", "wield bug"],
        setup=setup,
    )
    assert "You wield the Bug-Skin." in out
    assert "You're not carrying" not in out
    assert "You cannot wield" not in out
    assert p.wielded_weapon is not p.worn_armor


def test_inventory_commands_ignore_worn():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "bug-skin")

    out, w, p = run_commands(
        ["get bug", "wear bug", "drop bug", "convert bug", "wield bug"],
        setup=setup,
    )
    assert out.count("You're not carrying a Bug-Skin.") == 3
    assert "You are here." not in out and "Compass:" not in out
    assert p.worn_armor is not None


def test_remove_returns_worn_to_inventory():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "bug-skin")

    out, w, p = run_commands(
        ["get bug", "wear bug", "remove bug", "inventory"], setup=setup
    )
    assert "You remove the Bug-Skin." in out
    assert p.worn_armor is None
    assert any(coerce_item(i)["key"] == "bug-skin" for i in p.inventory)


def test_drop_and_convert_prefer_inventory_copy():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "bug-skin")
        w.add_ground_item(2000, 0, 0, "bug-skin")

    out, w, p = run_commands(
        ["get bug", "get bug", "wear bug", "drop bug"], setup=setup
    )
    assert "You drop Bug-Skin." in out
    assert "You're not carrying" not in out
    assert p.worn_armor is not None
    assert len(p.inventory) == 0
    assert sum(1 for it in w.ground[(2000, 0, 0)] if it["key"] == "bug-skin") == 1

    out, w, p = run_commands(
        ["get bug", "get bug", "wear bug", "convert bug"], setup=setup
    )
    assert "You convert the Bug-Skin into 22100 ions." in out
    assert "You're not carrying" not in out
    assert p.worn_armor is not None
    assert p.ions == 22100


def test_wield_armor_when_not_worn():
    def setup(w, p):
        w.add_ground_item(2000, 0, 0, "bug-skin")
        w.place_monster(2000, 0, 0, "mutant")

    out, w, p = run_commands(
        ["get bug", "combat mutant", "wield bug", "status"], setup=setup
    )
    assert "You wield the Bug-Skin." in out
    expected = items.REGISTRY["bug-skin"].base_power + p.strength // 10
    pattern = rf"You hit Mutant-\d{{4}} for {expected} damage\.  \(temp\)"
    assert re.search(pattern, out)
