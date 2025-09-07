from typing import Any, Union, cast

from mutants2.types import ItemInstance
from . import items as items_mod


def coerce_item(x: Union[ItemInstance, str]) -> ItemInstance:
    if isinstance(x, str):
        it: ItemInstance = {"key": x}
    else:
        key = str(x.get("key")) if "key" in x else ""
        it: ItemInstance = {"key": key}
        if "enchant" in x and x["enchant"] is not None:
            it["enchant"] = int(cast(int, x["enchant"]))
        if "base_power" in x and x["base_power"] is not None:
            it["base_power"] = int(cast(int, x["base_power"]))
        if "ac_bonus" in x and x["ac_bonus"] is not None:
            it["ac_bonus"] = int(cast(int, x["ac_bonus"]))
        if "meta" in x and x["meta"] is not None:
            it["meta"] = dict(cast(dict[str, Any], x["meta"]))
    if "enchant" not in it:
        item = items_mod.REGISTRY.get(it["key"])
        if item and item.default_enchant_level:
            it["enchant"] = item.default_enchant_level
    return it
