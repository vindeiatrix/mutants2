"""Simple combat helpers."""

from __future__ import annotations

import math

from types import SimpleNamespace

from .leveling import check_level_up
from . import items as items_mod
from .loot_flow import perform_loot_flow
from ..data.config import AC_DIVISOR

MONSTER_XP = 20_000


def award_kill(player) -> int:
    """Award XP for a monster kill and trigger level-up checks.

    Returns the amount of experience awarded.
    """

    player.exp += MONSTER_XP
    check_level_up(player)
    return MONSTER_XP



def _kill_monster(ctx: SimpleNamespace, world, player, mon, year: int, x: int, y: int) -> None:
    """Single entry point for handling monster deaths."""

    xp = award_kill(player)
    riblets = mon.get("riblets_reward", 20_000)
    ions = mon.get("ions_reward", 20_000)
    player.riblets += riblets
    player.ions += ions

    perform_loot_flow(
        world=world,
        player=player,
        monster=mon,
        tile=(year, x, y),
        xp=xp,
        riblets=riblets,
        ions=ions,
    )

    world.remove_monster(year, x, y)


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
        _kill_monster(ctx, w, p, mon, p.year, p.x, p.y)
    return dmg, killed, name
