from dataclasses import dataclass
from typing import Optional, Callable
import collections

from .types import ItemInstance
from ..ui.theme import yellow
from ..ui.wrap import wrap_paragraph_ansi
from ..ui.articles import article_for
from .util.names import norm_name

NBSP = "\u00a0"


@dataclass(frozen=True)
class ItemDef:
    key: str
    name: str
    weight_lbs: Optional[int] = None
    ion_value: Optional[int] = None
    riblets: Optional[int] = None
    spawnable: bool = False
    description_fn: Optional[Callable[[ItemInstance], str]] = None
    base_power: int = 0
    ac_bonus: int = 0
    default_enchant_level: int = 0
    convert_value_ions: Optional[int] = None


REGISTRY: dict[str, ItemDef] = {}


def _add(
    key,
    name,
    weight_lbs=None,
    ion_value=None,
    riblets=None,
    *,
    spawnable: bool = False,
    description_fn: Optional[Callable[[ItemInstance], str]] = None,
    base_power: int = 0,
    ac_bonus: int = 0,
    default_enchant_level: int = 0,
    convert_value_ions: Optional[int] = None,
):
    REGISTRY[key] = ItemDef(
        key,
        name,
        weight_lbs,
        ion_value,
        riblets,
        spawnable,
        description_fn,
        base_power,
        ac_bonus,
        default_enchant_level,
        convert_value_ions,
    )


# Populate spawnable items
_add(
    "nuclear_decay",
    "Nuclear-Decay",
    50,
    85000,
    60600,
    spawnable=True,
    base_power=77,
)
_add(
    "ion_decay",
    "Ion-Decay",
    10,
    18000,
    19140,
    spawnable=True,
    base_power=10,
)
_add(
    "nuclear_rock",
    "Nuclear-Rock",
    10,
    15000,
    49200,
    spawnable=True,
    base_power=7,
)
_add(
    "gold_chunk",
    "Gold-Chunk",
    25,
    25000,
    49800,
    spawnable=True,
    base_power=17,
)
_add("cheese", "Cheese", 1, 12000, 6060, spawnable=True, base_power=4)
_add(
    "light_spear",
    "Light-Spear",
    10,
    11000,
    None,
    spawnable=True,
    base_power=3,
)
_add(
    "monster_bait",
    "Monster-Bait",
    10,
    10000,
    spawnable=True,
    base_power=2,
)
_add(
    "nuclear_thong",
    "Nuclear-thong",
    20,
    13000,
    600,
    spawnable=True,
    base_power=5,
)
_add(
    "ion_pack",
    "Ion-Pack",
    50,
    20000,
    6,
    spawnable=True,
    base_power=12,
)
_add(
    "ion_booster",
    "Ion-Booster",
    10,
    13000,
    300,
    spawnable=True,
    base_power=5,
)
_add(
    "nuclear_waste",
    "Nuclear-Waste",
    30,
    15000,
    55200,
    spawnable=True,
    base_power=7,
)
_add(
    "cigarette_butt",
    "Cigarette-Butt",
    1,
    11000,
    606,
    spawnable=True,
    base_power=3,
)
_add(
    "bottle_cap",
    "Bottle-Cap",
    1,
    22000,
    606,
    spawnable=True,
    base_power=14,
)
_add(
    "bug-skin",
    "Bug-Skin",
    8,
    20000,
    spawnable=True,
    ac_bonus=3,
    default_enchant_level=1,
    convert_value_ions=22100,
)


def describe_skull(inst: ItemInstance) -> str:
    monster_type = inst.get("monster_type", "Unknown")
    text = (
        "A shiver is sent down your spine as you realize this is the skull "
        "of a victim that has lost in a bloody battle. Looking closer, you realize "
        f"this is the skull of a {monster_type}!"
    )
    return yellow(wrap_paragraph_ansi(text, 80))


_add(
    "skull",
    "Skull",
    5,
    25000,
    spawnable=False,
    description_fn=describe_skull,
    base_power=4,
)

SPAWNABLE_KEYS = [k for k, v in REGISTRY.items() if v.spawnable]

__all__ = [
    "ItemDef",
    "REGISTRY",
    "SPAWNABLE_KEYS",
    "find_by_name",
    "canon_item_key",
    "norm_name",
    "resolve_item_prefix",
    "resolve_prefix",
    "first_prefix_match",
    "describe",
    "article_name",
    "stack_for_render",
    "stack_plain",
    "resolve_key_prefix",
    "display_name",
    "describe_instance",
]


def find_by_name(name: str) -> Optional[ItemDef]:
    target = name.strip().lower()
    for item in REGISTRY.values():
        if item.name.lower() == target:
            return item
    return None


def canon_item_key(s: str) -> str:
    return s.strip().lower().replace(" ", "_").replace("-", "_")


def first_prefix_match(prefix: str, names_in_order: list[str]) -> str | None:
    """Return the first candidate whose name starts with ``prefix``.

    Prefix comparison is case-insensitive and accepts any prefix length from
    one up to the full name. The first match in ``names_in_order`` wins; no
    ambiguity errors are reported.
    """
    p = prefix.strip().lower()
    for name in names_in_order:
        if name.lower().startswith(p):
            return name
    return None


def resolve_item_prefix(
    query: str, candidates: list[str]
) -> tuple[Optional[str], list[str]]:
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


def resolve_prefix(
    query: str, ground_names: list[str], inv_names: list[str]
) -> Optional[str]:
    name, amb = resolve_item_prefix(query, ground_names + inv_names)
    if name and not amb:
        return name
    return None


def describe(name: str) -> str:
    item = find_by_name(name)
    if item:
        return f"You see {item.name}."
    return f"You see {name}."


def article_name(name: str) -> str:
    parts = name.split("-")
    t = "-".join(p[:1].upper() + p[1:] for p in parts)
    return f"{article_for(t)} {t}"


def stack_for_render(item_names: list[str]) -> list[str]:
    counts = collections.Counter(item_names)
    tokens: list[str] = []
    for name in item_names:
        if counts[name] == 0:
            continue
        if counts[name] == 1:
            tokens.append(article_name(name))
        else:
            tokens.append(article_name(name))
            tokens.append(f"{article_name(name)}{NBSP}({counts[name]-1})")
        counts[name] = 0
    if tokens:
        tokens[-1] = tokens[-1] + "."
    return tokens


def stack_plain(item_names: list[str]) -> list[str]:
    counts = collections.Counter(item_names)
    tokens: list[str] = []
    for name in item_names:
        if counts[name] == 0:
            continue
        if counts[name] == 1:
            tokens.append(name)
        else:
            tokens.append(name)
            tokens.append(f"{name}{NBSP}({counts[name]-1})")
        counts[name] = 0
    if tokens:
        tokens[-1] = tokens[-1] + "."
    return tokens


def resolve_key_prefix(query: str) -> Optional[str]:
    q = norm_name(query)
    if not q:
        return None
    matches = []
    for key, item in REGISTRY.items():
        if norm_name(key).startswith(q) or norm_name(item.name).startswith(q):
            matches.append(key)
    if len(matches) == 1:
        return matches[0]
    return None


def display_name(key: str) -> str:
    return REGISTRY[key].name


def describe_instance(inst: ItemInstance) -> str | None:
    item = REGISTRY.get(inst["key"])
    if item and item.description_fn:
        return item.description_fn(inst)
    return None


SPAWNABLE_KEYS = [k for k, v in REGISTRY.items() if v.spawnable]

__all__ = [
    "ItemDef",
    "REGISTRY",
    "SPAWNABLE_KEYS",
    "find_by_name",
    "canon_item_key",
    "norm_name",
    "first_prefix_match",
    "resolve_item_prefix",
    "resolve_prefix",
    "describe",
    "article_name",
    "stack_for_render",
    "stack_plain",
    "resolve_key_prefix",
    "display_name",
    "describe_instance",
]
