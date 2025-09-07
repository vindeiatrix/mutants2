from typing import Union

from mutants2.types import ItemInstance


def coerce_item(x: Union[ItemInstance, str]) -> ItemInstance:
    if isinstance(x, str):
        return {"key": x}

    out: ItemInstance = {"key": str(x.get("key", ""))}
    if "enchant" in x and x["enchant"] is not None:
        out["enchant"] = int(x["enchant"])
    if "base_power" in x and x["base_power"] is not None:
        out["base_power"] = int(x["base_power"])
    if "ac_bonus" in x and x["ac_bonus"] is not None:
        out["ac_bonus"] = int(x["ac_bonus"])
    if "meta" in x and isinstance(x["meta"], dict):
        out["meta"] = dict(x["meta"])
    return out
