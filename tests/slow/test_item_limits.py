from __future__ import annotations

import contextlib
from io import StringIO

from mutants2.cli.shell import make_context
from mutants2.engine import persistence
from mutants2.engine.player import Player, INVENTORY_LIMIT
from mutants2.engine.world import World
from mutants2.engine import items
from mutants2.ui.theme import yellow
from mutants2.ui.articles import article_for


def run(cmds: list[str], *, p: Player, w: World):
    save = persistence.Save()
    ctx = make_context(p, w, save)
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        for cmd in cmds:
            ctx.dispatch_line(cmd)
    return buf.getvalue()


def test_inventory_limit_swap():
    inv_keys = [
        "ion_decay",
        "gold_chunk",
        "cheese",
        "light_spear",
        "monster_bait",
        "nuclear_thong",
        "ion_pack",
        "ion_booster",
        "nuclear_waste",
        "cigarette_butt",
    ]
    p = Player()
    for k in inv_keys:
        p.inventory.append(k)
    w = World({(2000, 0, 0): ["bottle_cap"]}, {2000}, global_seed=123)

    out = run(["get Bottle-Cap"], p=p, w=w)

    assert len(p.inventory) == INVENTORY_LIMIT
    ground_items = w.items_on_ground(2000, 0, 0)
    assert len(ground_items) == 1
    victim_name = ground_items[0].name
    assert yellow("***") in out
    assert yellow(f"The {victim_name} fell out of your sack!") in out
    assert out.index(f"The {victim_name} fell out of your sack!") < out.index(
        "You pick up A Bottle-Cap."
    )


def test_ground_limit_swap():
    ground_keys = [
        "ion_decay",
        "gold_chunk",
        "cheese",
        "light_spear",
        "monster_bait",
        "nuclear_thong",
    ]
    w = World({(2000, 0, 0): ground_keys}, {2000}, global_seed=123)
    p = Player()
    p.inventory.append("cigarette_butt")

    out = run(["drop Cigarette-Butt"], p=p, w=w)

    assert len(w.items_on_ground(2000, 0, 0)) == 6
    assert len(p.inventory) == 1
    gift = p.inventory[0]
    gift_name = items.REGISTRY[gift["key"]].name
    assert yellow("***") in out
    assert (
        yellow(
            f"{article_for(gift_name)} {gift_name} has magically appeared in your hand!"
        )
        in out
    )
    assert out.index("You drop A Cigarette-Butt.") < out.index(
        f"{article_for(gift_name)} {gift_name} has magically appeared in your hand!"
    )
