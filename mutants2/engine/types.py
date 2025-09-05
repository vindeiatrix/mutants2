from __future__ import annotations

from typing import Mapping, MutableMapping, Sequence, Tuple, Literal, TYPE_CHECKING, Union

if TYPE_CHECKING:  # pragma: no cover
    from .state import ItemInstance

TileKey = Tuple[int, int, int]
Direction = Literal["north", "south", "east", "west"]
ItemList = Sequence[Union[str, "ItemInstance"]]
ItemListMut = list[Union[str, "ItemInstance"]]
MonsterRec = Mapping[str, object]
MonsterList = Sequence[MonsterRec]


def mk_key(x: int, y: int, year: int) -> TileKey:
    return (x, y, year)
