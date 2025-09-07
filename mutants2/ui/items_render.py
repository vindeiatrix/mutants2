from mutants2.types import ItemInstance
from mutants2.engine.items import ItemDef


def _base_item_name(it: ItemInstance, idef: ItemDef | None) -> str:
    """Return the canonical display name for an item without enchant."""
    if idef:
        return idef.name
    return (
        it.get("key", "").replace("_", " ")
        .replace("-", " ")
        .title()
        .replace(" ", "-")
    )


def display_item_name_plain(it: ItemInstance, idef: ItemDef | None) -> str:
    """Display helper for inventory and stats (no +N prefix)."""
    return _base_item_name(it, idef)


def display_item_name_with_plus(it: ItemInstance, idef: ItemDef | None) -> str:
    """Display helper for look command (includes +N when enchanted)."""
    base = _base_item_name(it, idef)
    n = (
        it.get("meta", {}).get("enchant_level")
        or it.get("enchant")
        or 0
    )
    if n > 0:
        return f"+{n} {base}"
    return base
