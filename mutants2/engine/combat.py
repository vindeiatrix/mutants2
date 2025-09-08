"""Simple combat helpers."""

from __future__ import annotations

import math

from .leveling import check_level_up
from . import items as items_mod
from ..data.config import AC_DIVISOR
from ..ui.render import render_kill_block
from ..ui.theme import SEP
from ..ui.strings import kill_reward

MONSTER_XP = 20_000


def award_kill(player) -> int:
    """Award XP for a monster kill and trigger level-up checks.

    Returns the amount of experience awarded.
    """

    player.exp += MONSTER_XP
    check_level_up(player)
    return MONSTER_XP


def player_attack(player, world, weapon_key: str):
    """Perform a single attack against the first monster here.

    Returns ``(damage, killed, name)`` where ``name`` is the monster's name.
    """

    mon = world.monster_here(player.year, player.x, player.y)
    if not mon:
        return 0, False, ""
    item = items_mod.REGISTRY.get(weapon_key)
    base = item.base_power if item else 0
    str_bonus = player.strength // 10
    defender_ac = int(mon.get("ac_total", 0))
    ac_red = math.floor(defender_ac / AC_DIVISOR)
    raw = base + str_bonus - ac_red
    dmg = max(1, raw)
    name = str(mon.get("name", ""))
    killed = world.damage_monster(player.year, player.x, player.y, dmg, player)
    if killed:
        ions = 20_000
        riblets = 20_000
        player.ions += ions
        player.riblets += riblets
        award_kill(player)
        render_kill_block(riblets, ions)
        print(SEP)
        print(kill_reward(f"{name} is crumbling to dust!"))
    return dmg, killed, name
