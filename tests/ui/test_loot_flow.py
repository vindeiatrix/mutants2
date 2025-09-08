import contextlib
import io
import re
from types import SimpleNamespace

from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.engine.combat import player_attack
from mutants2.ui.theme import red, SEP


def test_loot_flow_single_line_and_crumble():
    w = World()
    w.year(2000)
    w.place_monster(2000, 0, 0, "mutant")
    p = Player(year=2000, clazz="Warrior")
    ctx = SimpleNamespace(player=p, world=w)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        player_attack(ctx, "nuclear_rock")
    out = buf.getvalue()
    assert re.search(r"\x1b\[31mYou have slain Mutant-\d{4}!\x1b\[0m", out)
    assert re.search(
        r"\x1b\[31mYour experience points are increased by 20000!\x1b\[0m",
        out,
    )
    assert red("You collect 20000 Riblets and 20000 ions from the slain body.") in out
    assert re.search(
        rf"{re.escape(SEP)}\n\x1b\[37mA Skull is falling from Mutant-\d{{4}}'s body!\x1b\[0m\n{re.escape(SEP)}\n\x1b\[31mMutant-\d{{4}} is crumbling to dust!\x1b\[0m",
        out,
    )
    assert re.search(r"\x1b\[31mA Skull is falling", out) is None
