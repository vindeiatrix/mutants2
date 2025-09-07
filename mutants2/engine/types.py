from __future__ import annotations

from typing import Mapping, Sequence, Tuple, Literal, NotRequired, Required, TypedDict

TileKey = Tuple[int, int, int]


class ItemInstance(TypedDict, total=False):
    key: Required[str]
    enchant: NotRequired[int]
    base_power: NotRequired[int]
    ac_bonus: NotRequired[int]
    weight_lbs: NotRequired[int]


class MonsterInstance(TypedDict, total=False):
    kind: Required[str]
    id: Required[str]
    pos: Required[TileKey]
    aggro: Required[bool]
    seen: Required[bool]
    yelled_once: NotRequired[bool]
    level: Required[int]
    STR: Required[int]
    INT: Required[int]
    WIS: Required[int]
    DEX: Required[int]
    CON: Required[int]
    CHA: Required[int]
    worn_armor: NotRequired[ItemInstance]
    wielded_weapon: NotRequired[ItemInstance]
    inventory: NotRequired[list[ItemInstance]]


class SaveDoc(TypedDict, total=False):
    schema: Required[int]
    global_seed: Required[int]
    last_topup_date: Required[str]


Direction = Literal["north", "south", "east", "west"]
ItemList = Sequence[ItemInstance]
ItemListMut = list[ItemInstance]
MonsterRec = Mapping[str, object]
MonsterList = Sequence[MonsterRec]

__all__ = [
    "TileKey",
    "ItemInstance",
    "MonsterInstance",
    "SaveDoc",
    "Direction",
    "ItemList",
    "ItemListMut",
    "MonsterRec",
    "MonsterList",
]
