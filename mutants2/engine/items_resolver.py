from __future__ import annotations

import re
from mutants2.engine import items as items_mod
from typing import Iterable, Literal, TYPE_CHECKING


def normalize_token(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[\s_\-]+", " ", s)
    return s


def resolve_key(raw: str) -> str:
    if raw in items_mod.REGISTRY:
        return raw
    t = normalize_token(raw)
    return t.replace(" ", "_")


def get_item_def_by_key(raw_key: str):
    key = resolve_key(raw_key)
    return items_mod.REGISTRY.get(key)


def resolve_key_prefix(
    query: str, candidates: Iterable[str] | None = None
) -> str | None:
    t = normalize_token(query)
    if not t:
        return None
    canon = t.replace(" ", "_")
    search = candidates if candidates is not None else items_mod.REGISTRY.keys()
    if canon in search and canon in items_mod.REGISTRY:
        return canon
    matches = []
    for key in search:
        item = items_mod.REGISTRY.get(key)
        if not item:
            continue
        name_token = normalize_token(item.name).replace(" ", "_")
        if key.startswith(canon) or name_token.startswith(canon):
            matches.append(key)
    if matches:
        if len(matches) == 1 or candidates is not None:
            return matches[0]
    return None


if TYPE_CHECKING:  # pragma: no cover - import cycle guard
    from .player import Player
    from .world import World
    from .types import ItemInstance


def resolve_item(
    prefix: str,
    scope: Literal["inventory", "worn", "ground"],
    player: Player,
    world: World,
) -> ItemInstance | str | None:
    """Resolve ``prefix`` to an item instance within ``scope``."""

    from .items_util import coerce_item  # local import to avoid cycles

    if scope == "inventory":
        keys = [resolve_key(coerce_item(obj)["key"]) for obj in player.inventory]
        key = resolve_key_prefix(prefix, keys)
        if not key:
            return None
        for obj in player.inventory:
            inst = coerce_item(obj)
            if resolve_key(inst["key"]) == key:
                return obj
        return None

    if scope == "worn":
        if not player.worn_armor:
            return None
        inst = coerce_item(player.worn_armor)
        key = resolve_key(inst["key"])
        return player.worn_armor if resolve_key_prefix(prefix, [key]) == key else None

    if scope == "ground":
        items = world.ground.get((player.year, player.x, player.y), [])
        keys = [resolve_key(coerce_item(obj)["key"]) for obj in items]
        key = resolve_key_prefix(prefix, keys)
        if not key:
            return None
        for obj in items:
            inst = coerce_item(obj)
            if resolve_key(inst["key"]) == key:
                return obj
        return None

    return None
