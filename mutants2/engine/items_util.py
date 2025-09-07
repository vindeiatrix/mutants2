from typing import Union, cast

from . import items as items_mod
from .types import ItemInstance


def coerce_item(x: Union[ItemInstance, str]) -> ItemInstance:
    if isinstance(x, dict):
        inst = cast(ItemInstance, x)
    else:
        inst: ItemInstance = {"key": x}
    if "enchant" not in inst:
        item = items_mod.REGISTRY.get(inst["key"])
        if item and item.default_enchant_level:
            inst["enchant"] = item.default_enchant_level
    return inst
