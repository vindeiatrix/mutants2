from mutants2.engine.items import ItemDef
from mutants2.types import ItemInstance


def display_item_name_plain(it: ItemInstance, idef: ItemDef | None) -> str:
    base = (
        (idef.name if idef else it.get("key", ""))
        .replace("-", " ")
        .title()
        .replace(" ", "-")
    )
    return base


def display_item_name_with_plus(it: ItemInstance, idef: ItemDef | None) -> str:
    name = display_item_name_plain(it, idef)
    n = it.get("enchant") or 0
    return f"+{n} {name}" if n > 0 else name
