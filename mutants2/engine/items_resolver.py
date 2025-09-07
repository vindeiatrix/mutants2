import re
from mutants2.engine import items as items_mod
from typing import Iterable

LEGACY_KEY_MAP = {
    "bug_skin_armour": "bug-skin",
    "bug_skin_armor": "bug-skin",
    "bug-skin-armour": "bug-skin",
    "bug-skin-armor": "bug-skin",
    "bug skin armour": "bug-skin",
    "bug skin armor": "bug-skin",
    "bugskin": "bug-skin",
}

def normalize_token(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[\s_\-]+", " ", s)
    return s

def resolve_key(raw: str) -> str:
    if raw in items_mod.REGISTRY:
        return raw
    t = normalize_token(raw)
    if t in LEGACY_KEY_MAP:
        return LEGACY_KEY_MAP[t]
    return t.replace(" ", "_")

def get_item_def_by_key(raw_key: str):
    key = resolve_key(raw_key)
    return items_mod.REGISTRY.get(key)


def resolve_key_prefix(query: str, candidates: Iterable[str] | None = None) -> str | None:
    t = normalize_token(query)
    if not t:
        return None
    alias = LEGACY_KEY_MAP.get(t)
    if alias:
        return alias
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
