from typing import Union

from mutants2.types import ItemInstance


def coerce_item(x: Union[ItemInstance, str]) -> ItemInstance:
    if isinstance(x, dict):
        return x
    return {"key": x, "enchant": None, "base_power": None, "ac_bonus": None, "meta": {}}
