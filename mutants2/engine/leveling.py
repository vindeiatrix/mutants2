"""Level computation and application of per-level gains."""

from __future__ import annotations

from .classes import xp_to_level, gains_for_level
from ..ui.theme import yellow


def check_level_up(player) -> None:
    """Recompute the player's level based on ``player.exp``.

    If one or more level thresholds are crossed the appropriate stat and HP
    gains are applied and a message is printed for each level advanced.
    """

    if not player.clazz:
        return
    target = xp_to_level(player.clazz, player.exp)
    while player.level < target:
        player.level += 1
        gains = gains_for_level(player.clazz, player.level)
        player.strength += gains.str
        player.intelligence += gains.int
        player.wisdom += gains.wis
        player.dexterity += gains.dex
        player.constitution += gains.con
        player.charisma += gains.cha
        if gains.hp:
            player.max_hp += gains.hp
            player.hp += gains.hp
        print(yellow("***"))
        print(yellow(f"You advance to Level {player.level}!"))
