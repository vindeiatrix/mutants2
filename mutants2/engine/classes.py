"""Class defaults loaded from data tables."""

from __future__ import annotations

from ..data.class_tables import BASE_LEVEL1

_ATTR_MAP = {
    "str": "strength",
    "int": "intelligence",
    "wis": "wisdom",
    "dex": "dexterity",
    "con": "constitution",
    "cha": "charisma",
}


def apply_class_defaults(player, clazz: str) -> None:
    """Reset ``player`` to the starting stats for ``clazz``."""

    base = BASE_LEVEL1[clazz]
    for key, attr in _ATTR_MAP.items():
        setattr(player, attr, base[key])
    player.max_hp = base["hp"]
    player.hp = base["hp"]
    player.ac = base["ac"]
    player.exp = 0
    player.level = 1
    player.recompute_ac()
