import contextlib
import io
import re

from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.engine.combat import player_attack
from mutants2.ui.theme import red


def test_loot_flow_single_line_and_crumble():
    w = World()
    w.year(2000)
    w.place_monster(2000, 0, 0, "mutant")
    p = Player(year=2000, clazz="Warrior")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        player_attack(p, w, "nuclear_rock")
    out = buf.getvalue()
    assert red("You collect 20000 Riblets and 20000 ions from the slain body.") in out
    assert re.search(r"You gain \d+ riblets", out) is None
    assert re.search(
        r"\x1b\[37m\*\*\*\x1b\[0m\n\x1b\[31mMutant-\d{4} is crumbling to dust!\x1b\[0m",
        out,
    )
