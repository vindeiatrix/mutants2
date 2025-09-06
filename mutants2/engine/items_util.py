from typing import Union

from mutants2.types import ItemInstance
from . import items as items_mod


def coerce_item(x: Union[ItemInstance, str]) -> ItemInstance:
    if isinstance(x, dict):
        inst = x
    else:
        inst = {"key": x, "enchant": None, "base_power": None, "ac_bonus": None, "meta": {}}
    meta = inst.setdefault("meta", {})
    if "enchant_level" not in meta:
        item = items_mod.REGISTRY.get(inst["key"])
        if item and item.default_enchant_level:
            meta["enchant_level"] = item.default_enchant_level
    return inst
