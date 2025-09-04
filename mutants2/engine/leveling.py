"""Level computation and application of per-level gains."""
from __future__ import annotations

from ..data.class_tables import PROGRESSION
from ..ui.theme import yellow
from .player import class_key

_ATTR_MAP = {
    "str": "strength",
    "int": "intelligence",
    "wis": "wisdom",
    "dex": "dexterity",
    "con": "constitution",
    "cha": "charisma",
}


def _xp_for_level(clazz: str, level: int) -> int:
    table = PROGRESSION[clazz]
    if level in table:
        return table[level]["xp_to_reach"]
    xp11 = table[11]["xp_to_reach"]
    return (level - 10) * xp11


def check_level_up(player) -> None:
    """Recompute the player's level based on ``player.exp``."""

    if not player.clazz:
        return
    clazz = class_key(player.clazz)
    table = PROGRESSION.get(clazz, {})
    while True:
        next_level = player.level + 1
        xp_needed = _xp_for_level(clazz, next_level)
        if player.exp < xp_needed:
            break
        deltas = table.get(next_level, table.get(11, {}))
        player.max_hp += deltas.get("hp_plus", 0)
        if player.hp > player.max_hp:
            player.hp = player.max_hp
        for short, attr in _ATTR_MAP.items():
            inc = deltas.get(f"{short}_plus", 0)
            setattr(player, attr, getattr(player, attr) + inc)
        player.level = next_level
        print(yellow("***"))
        print(yellow(f"You advance to Level {player.level}!"))
