from __future__ import annotations

from typing import Mapping, MutableMapping, Sequence, Tuple, Literal

TileKey = Tuple[int, int, int]
Direction = Literal["north", "south", "east", "west"]
ItemList = Sequence[str]
ItemListMut = list[str]
MonsterRec = Mapping[str, object]
MonsterList = Sequence[MonsterRec]


def mk_key(x: int, y: int, year: int) -> TileKey:
    return (x, y, year)
