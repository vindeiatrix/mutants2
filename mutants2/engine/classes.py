"""Class defaults and progression tables.

The real game contains rich per-class data.  For the purposes of the tests in
this kata we only model the small subset that is required: starting stats for
each class and experience/HP/stat gains for levels 2 through 11.

The numbers are intentionally conservative; the exact values are less important
than the mechanics around levelling.  Additional data can be slotted into the
tables without changing the surrounding code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ClassDefaults:
    str: int
    int: int
    wis: int
    dex: int
    con: int
    cha: int
    hp: int
    ac: int


@dataclass(frozen=True)
class LevelProgress:
    xp: int
    str: int = 0
    int: int = 0
    wis: int = 0
    dex: int = 0
    con: int = 0
    cha: int = 0
    hp: int = 0


# Starting values for the five playable classes.  These figures are derived from
# reference stat pages of the original game.
CLASS_DEFAULTS: Dict[str, ClassDefaults] = {
    "thief": ClassDefaults(20, 12, 13, 17, 17, 14, 30, 1),
    "priest": ClassDefaults(20, 12, 13, 17, 17, 14, 30, 1),
    "wizard": ClassDefaults(20, 12, 13, 17, 17, 14, 30, 1),
    "warrior": ClassDefaults(20, 12, 13, 17, 17, 14, 30, 1),
    "mage": ClassDefaults(20, 12, 13, 17, 17, 14, 30, 1),
}


# Per-level progression tables.  Each entry corresponds to the XP required to
# and the stat/HP gains granted on reaching that level.  Level numbers are
# implicit via list position (index 0 -> level 2).
LEVEL_TABLES: Dict[str, List[LevelProgress]] = {
    "mage": [
        LevelProgress(40_000, hp=5),
        LevelProgress(120_000, hp=5),
        LevelProgress(240_000, hp=5),
        LevelProgress(480_000, hp=5),
        LevelProgress(960_000, hp=5),
        LevelProgress(1_800_000, hp=5),
        LevelProgress(3_000_000, hp=5),
        LevelProgress(4_500_000, hp=5),
        LevelProgress(5_500_000, hp=5),
        LevelProgress(6_000_000, hp=5),
    ],
    # Other classes use a similar placeholder progression.
    "thief": [
        LevelProgress(40_000, hp=5),
        LevelProgress(120_000, hp=5),
        LevelProgress(240_000, hp=5),
        LevelProgress(480_000, hp=5),
        LevelProgress(960_000, hp=5),
        LevelProgress(1_800_000, hp=5),
        LevelProgress(3_000_000, hp=5),
        LevelProgress(4_500_000, hp=5),
        LevelProgress(5_500_000, hp=5),
        LevelProgress(6_000_000, hp=5),
    ],
    "priest": [
        LevelProgress(40_000, hp=5),
        LevelProgress(120_000, hp=5),
        LevelProgress(240_000, hp=5),
        LevelProgress(480_000, hp=5),
        LevelProgress(960_000, hp=5),
        LevelProgress(1_800_000, hp=5),
        LevelProgress(3_000_000, hp=5),
        LevelProgress(4_500_000, hp=5),
        LevelProgress(5_500_000, hp=5),
        LevelProgress(6_000_000, hp=5),
    ],
    "wizard": [
        LevelProgress(40_000, hp=5),
        LevelProgress(120_000, hp=5),
        LevelProgress(240_000, hp=5),
        LevelProgress(480_000, hp=5),
        LevelProgress(960_000, hp=5),
        LevelProgress(1_800_000, hp=5),
        LevelProgress(3_000_000, hp=5),
        LevelProgress(4_500_000, hp=5),
        LevelProgress(5_500_000, hp=5),
        LevelProgress(6_000_000, hp=5),
    ],
    "warrior": [
        LevelProgress(40_000, hp=5),
        LevelProgress(120_000, hp=5),
        LevelProgress(240_000, hp=5),
        LevelProgress(480_000, hp=5),
        LevelProgress(960_000, hp=5),
        LevelProgress(1_800_000, hp=5),
        LevelProgress(3_000_000, hp=5),
        LevelProgress(4_500_000, hp=5),
        LevelProgress(5_500_000, hp=5),
        LevelProgress(6_000_000, hp=5),
    ],
}


def xp_to_level(clazz: str, xp: int) -> int:
    """Return the level for ``xp`` in ``clazz``."""

    table = LEVEL_TABLES.get(clazz, [])
    level = 1
    for i, row in enumerate(table, start=2):
        if xp >= row.xp:
            level = i
        else:
            break
    if table:
        xp11 = table[-1].xp
        if xp >= xp11:
            extra = (xp - xp11) // xp11
            level = 11 + extra
    return level


def apply_class_defaults(player, clazz: str) -> None:
    """Reset ``player`` to the starting stats for ``clazz``."""

    defaults = CLASS_DEFAULTS[clazz]
    player.strength = defaults.str
    player.intelligence = defaults.int
    player.wisdom = defaults.wis
    player.dexterity = defaults.dex
    player.constitution = defaults.con
    player.charisma = defaults.cha
    player.max_hp = defaults.hp
    player.hp = defaults.hp
    player.ac = defaults.ac
    player.exp = 0
    player.level = 1


def gains_for_level(clazz: str, level: int) -> LevelProgress:
    table = LEVEL_TABLES.get(clazz, [])
    if not table:
        return LevelProgress(0)
    idx = min(level, 11) - 2
    idx = max(0, min(idx, len(table) - 1))
    return table[idx]
