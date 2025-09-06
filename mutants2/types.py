from typing import TypedDict, Tuple, Sequence, Mapping, Any, Required

TileKey = Tuple[int, int, int]


class ItemInstance(TypedDict, total=False):
    key: Required[str]
    enchant: int | None
    base_power: int | None
    ac_bonus: int | None
    meta: dict[str, Any]
