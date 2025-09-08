"""Simple combat helpers."""

from __future__ import annotations

import math

from types import SimpleNamespace

from .leveling import check_level_up
from . import items as items_mod, monsters as monsters_mod
from .items_util import coerce_item
from ..ui.items_render import display_item_name_plain
from ..engine.items_resolver import get_item_def_by_key
from ..ui.articles import article_for
from ..data.config import AC_DIVISOR
from ..ui.render import render_kill_block
from ..ui.theme import SEP, COLOR_DROP_ITEM
from ..ui.strings import kill_reward
from .player import GROUND_LIMIT

MONSTER_XP = 20_000


def award_kill(player) -> int:
    """Award XP for a monster kill and trigger level-up checks.

    Returns the amount of experience awarded.
    """

    player.exp += MONSTER_XP
    check_level_up(player)
    return MONSTER_XP


def handle_monster_death(ctx: SimpleNamespace, mon) -> None:
    """Handle XP, loot drops, and crumble messaging for a slain monster."""

    p = ctx.player
    w = ctx.world

    ions = 20_000
    riblets = 20_000
    p.ions += ions
    p.riblets += riblets
    xp = award_kill(p)
    name = str(mon.get("name", ""))

    print(kill_reward(f"You have slain {name}!"))
    print(kill_reward(f"Your experience points are increased by {xp}!"))
    render_kill_block(riblets, ions)

    drops = [coerce_item(d) for d in mon.get("gear", [])]
    mdef = monsters_mod.REGISTRY.get(mon.get("key"))
    mtype = mdef.name if mdef else "Unknown"
    drops.append({"key": "skull", "monster_type": mtype})
    worn = mon.get("worn_armor")
    if worn:
        drops.append(coerce_item(worn))

    have = len(w.items_on_ground(p.year, p.x, p.y))
    free = max(0, GROUND_LIMIT - have)
    drops = drops[:free]

    if drops:
        print(SEP)
    for i, inst in enumerate(drops):
        w.add_ground_item(p.year, p.x, p.y, inst)
        idef = get_item_def_by_key(inst["key"])
        iname = display_item_name_plain(inst, idef)
        art = article_for(iname)
        print(COLOR_DROP_ITEM(f"{art} {iname} is falling from {name}'s body!"))
        if i < len(drops) - 1:
            print(SEP)

    print(SEP)
    print(kill_reward(f"{name} is crumbling to dust!"))


def player_attack(ctx: SimpleNamespace, weapon_key: str):
    """Perform a single attack against the first monster here.

    Returns ``(damage, killed, name)`` where ``name`` is the monster's name.
    """

    p = ctx.player
    w = ctx.world

    mon = w.monster_here(p.year, p.x, p.y)
    if not mon:
        return 0, False, ""
    item = items_mod.REGISTRY.get(weapon_key)
    base = item.base_power if item else 0
    str_bonus = p.strength // 10
    defender_ac = int(mon.get("ac_total", 0))
    ac_red = math.floor(defender_ac / AC_DIVISOR)
    raw = base + str_bonus - ac_red
    dmg = max(1, raw)
    name = str(mon.get("name", ""))
    killed = w.damage_monster(p.year, p.x, p.y, dmg, p)
    if killed:
        handle_monster_death(ctx, mon)
    return dmg, killed, name
