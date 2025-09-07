"""Canonical TypedDict schemas used across the project.

The goal of this module is to provide a single source of truth for the
structures persisted to disk or exchanged between internal modules. The
schemas deliberately keep the number of fields to a minimum and avoid any
legacy aliases or optional behaviour. Public APIs should use ``Mapping`` or
``Sequence`` when consuming these types while the engine may mutate the
underlying ``dict``/``list`` instances as needed.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict, Tuple

TileKey = Tuple[int, int, int]


class ItemInstance(TypedDict, total=False):
    """A concrete item in the world or inventory."""

    # Canonical registry key (hyphenated)
    key: str
    enchant: NotRequired[int]
    base_power: NotRequired[int]
    ac_bonus: NotRequired[int]
    weight_lbs: NotRequired[int]


class MonsterInstance(TypedDict, total=False):
    """Serialized monster instance."""

    kind: str  # canonical monster key
    id: str  # stable per-entity id for suffix
    pos: TileKey
    aggro: bool
    seen: bool
    yelled_once: NotRequired[bool]
    level: int
    STR: int
    INT: int
    WIS: int
    DEX: int
    CON: int
    CHA: int
    worn_armor: NotRequired[ItemInstance]
    wielded_weapon: NotRequired[ItemInstance]
    inventory: NotRequired[list[ItemInstance]]


class SaveDoc(TypedDict, total=False):
    """Minimal save file structure written to disk."""

    schema: int
    global_seed: int
    last_topup_date: str
    # add minimal, explicit fields only
