from mutants2.types import ItemInstance
from mutants2.engine.items import ItemDef


def display_item_name(it: ItemInstance, idef: ItemDef | None, include_enchant: bool = True) -> str:
    if idef:
        base = idef.name
    else:
        base = (
            it.get("key", "").replace("_", " ").replace("-", " ").title().replace(" ", "-")
        )
    n = (
        it.get("meta", {}).get("enchant_level")
        or it.get("enchant")
        or 0
    )
    if include_enchant and n > 0:
        return f"+{n} {base}"
    return base
