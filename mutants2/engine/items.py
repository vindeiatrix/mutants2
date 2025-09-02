from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class ItemDef:
    key: str
    name: str
    ions: Optional[int] = None
    riblets: Optional[int] = None
    tags: tuple[str, ...] = ()


REGISTRY: dict[str, ItemDef] = {}


def _add(key, name, ions=None, riblets=None, tags=("spawnable",)):
    REGISTRY[key] = ItemDef(key, name, ions, riblets, tags)


# Populate spawnable items
_add("nuclear_decay",  "Nuclear-Decay", 85000, 60600)
_add("ion_decay",      "Ion-Decay",     18000, 19140)
_add("nuclear_rock",   "Nuclear-Rock",  15000, 49200)
_add("gold_chunk",     "Gold-Chunk",    25000, 49800)
_add("cheese",         "Cheese",        12000, 6060)
_add("light_spear",    "Light-Spear",   None,  None)
_add("monster_bait",   "Monster-Bait",  None,  None)
_add("nuclear_thong",  "Nuclear-thong", 13000, 600)
_add("ion_pack",       "Ion-Pack",      20000, 6)
_add("ion_booster",    "Ion-Booster",   13000, 300)
_add("nuclear_waste",  "Nuclear-Waste", 15000, 55200)
_add("cigarette_butt", "Cigarette-Butt",11000, 606)
_add("bottle_cap",     "Bottle-Cap",    22000, 606)

SPAWNABLE_KEYS = [k for k, v in REGISTRY.items() if "spawnable" in v.tags]

__all__ = [
    "ItemDef",
    "REGISTRY",
    "SPAWNABLE_KEYS",
    "find_by_name",
    "norm_name",
    "resolve_item_prefix",
    "resolve_prefix",
    "describe",
]


def find_by_name(name: str) -> Optional[ItemDef]:
    target = name.strip().lower()
    for item in REGISTRY.values():
        if item.name.lower() == target:
            return item
    return None


def norm_name(s: str) -> str:
    """Normalize an item name for case-insensitive prefix matching."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def resolve_item_prefix(query: str, candidates: list[str]) -> tuple[Optional[str], list[str]]:
    """Resolve ``query`` against ``candidates`` by prefix.

    Returns a tuple of ``(match, ambiguous)`` where ``match`` is the matched
    candidate name or ``None``.  ``ambiguous`` is a (possibly empty) list of
    candidate names that matched when the query was ambiguous.  At most the
    first 6 ambiguous matches are returned.
    """

    q = norm_name(query)
    if not q:
        return None, []
    matches = [name for name in candidates if norm_name(name).startswith(q)]
    if len(matches) == 1:
        return matches[0], []
    if not matches:
        return None, []
    return None, matches[:6]


def resolve_prefix(query: str, ground_names: list[str], inv_names: list[str]) -> Optional[str]:
    name, amb = resolve_item_prefix(query, ground_names + inv_names)
    if name and not amb:
        return name
    return None


def describe(name: str) -> str:
    item = find_by_name(name)
    if item:
        return f"You see {item.name}."
    return f"You see {name}."

