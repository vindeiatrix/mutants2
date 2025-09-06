from __future__ import annotations

from typing import Mapping, MutableMapping, Sequence, Tuple, Literal

from mutants2.types import TileKey, ItemInstance
Direction = Literal["north", "south", "east", "west"]
ItemList = Sequence[ItemInstance]
ItemListMut = list[ItemInstance]
MonsterRec = Mapping[str, object]
MonsterList = Sequence[MonsterRec]


def mk_key(x: int, y: int, year: int) -> TileKey:
    return (x, y, year)
