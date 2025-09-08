import contextlib
import io
import re
from types import SimpleNamespace

from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.engine.combat import player_attack
from mutants2.ui.theme import red, SEP


def run_kill(setup):
    w = World()
    w.year(2000)
    w.place_monster(2000, 0, 0, "mutant")
    mon = w.monster_here(2000, 0, 0)
    p = Player(year=2000, clazz="Warrior")
    if setup:
        setup(w, p, mon)
    ctx = SimpleNamespace(player=p, world=w)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        player_attack(ctx, "nuclear_rock")
    return buf.getvalue()


def test_no_space_no_drops():
    def setup(w, p, mon):
        for key in [
            "nuclear_decay",
            "ion_decay",
            "gold_chunk",
            "cheese",
            "light_spear",
            "monster_bait",
        ]:
            w.add_ground_item(2000, 0, 0, {"key": key})
        mon["gear"] = [{"key": "nuclear_rock"}]
        mon["worn_armor"] = {"key": "ion_pack"}

    out = run_kill(setup)
    assert re.search(r"\x1b\[31mYou have slain Mutant-\d{4}!\x1b\[0m", out)
    assert re.search(
        r"\x1b\[31mYour experience points are increased by 20000!\x1b\[0m",
        out,
    )
    assert red("You collect 20000 Riblets and 20000 ions from the slain body.") in out
    assert re.search(r"is falling from", out) is None
    assert re.search(
        rf"{re.escape(SEP)}\n\x1b\[31mMutant-\d{{4}} is crumbling to dust!\x1b\[0m",
        out,
    )


def test_partial_space_first_item_only():
    def setup(w, p, mon):
        for key in [
            "nuclear_decay",
            "ion_decay",
            "gold_chunk",
            "cheese",
            "light_spear",
        ]:
            w.add_ground_item(2000, 0, 0, {"key": key})
        mon["gear"] = [{"key": "nuclear_rock"}, {"key": "gold_chunk"}]
        mon["worn_armor"] = {"key": "monster_bait"}

    out = run_kill(setup)
    assert re.search(
        rf"{re.escape(SEP)}\n\x1b\[37mA Nuclear-Rock is falling from Mutant-\d{{4}}'s body!\x1b\[0m\n{re.escape(SEP)}",
        out,
    )
    assert "Gold-Chunk is falling" not in out
    assert "Skull is falling" not in out
    assert "Monster-Bait is falling" not in out


def test_full_space_ordered_truncation():
    def setup(w, p, mon):
        mon["gear"] = [{"key": "nuclear_rock"}, {"key": "gold_chunk"}]
        mon["worn_armor"] = {"key": "monster_bait"}

    out = run_kill(setup)
    pattern = (
        rf"{re.escape(SEP)}\n"
        rf"\x1b\[37mA Nuclear-Rock is falling from Mutant-\d{{4}}'s body!\x1b\[0m\n{re.escape(SEP)}\n"
        rf"\x1b\[37mA Gold-Chunk is falling from Mutant-\d{{4}}'s body!\x1b\[0m\n{re.escape(SEP)}\n"
        rf"\x1b\[37mA Skull is falling from Mutant-\d{{4}}'s body!\x1b\[0m\n{re.escape(SEP)}\n"
        rf"\x1b\[37mA Monster-Bait is falling from Mutant-\d{{4}}'s body!\x1b\[0m\n{re.escape(SEP)}"
    )
    assert re.search(pattern, out)
    assert re.search(r"\x1b\[31m.*is falling", out) is None
    assert re.search(
        r"\x1b\[31mMutant-\d{4} is crumbling to dust!\x1b\[0m",
        out,
    )


def test_skull_only_with_space():
    def setup(w, p, mon):
        mon["gear"] = []

    out = run_kill(setup)
    assert re.search(
        rf"{re.escape(SEP)}\n\x1b\[37mA Skull is falling from Mutant-\d{{4}}'s body!\x1b\[0m",
        out,
    )


def test_skull_only_no_space():
    def setup(w, p, mon):
        for key in [
            "nuclear_decay",
            "ion_decay",
            "gold_chunk",
            "cheese",
            "light_spear",
            "monster_bait",
        ]:
            w.add_ground_item(2000, 0, 0, {"key": key})
        mon["gear"] = []

    out = run_kill(setup)
    assert re.search(r"is falling from", out) is None
