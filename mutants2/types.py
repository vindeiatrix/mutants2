from typing import TypedDict, Tuple, Any, NotRequired, Required

TileKey = Tuple[int, int, int]


class ItemInstance(TypedDict, total=False):
    key: Required[str]
    enchant: NotRequired[int]
    base_power: NotRequired[int]
    ac_bonus: NotRequired[int]
    meta: NotRequired[dict[str, Any]]
