from dataclasses import dataclass
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


def find_by_name(name: str) -> Optional[ItemDef]:
    target = name.strip().lower()
    for item in REGISTRY.values():
        if item.name.lower() == target:
            return item
    return None
