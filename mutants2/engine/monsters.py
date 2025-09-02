from dataclasses import dataclass

from .items import norm_name


@dataclass(frozen=True)
class MonsterDef:
    key: str
    name: str
    base_hp: int = 3  # small, so combat resolves quickly


REGISTRY = {
    "mutant": MonsterDef("mutant", "Mutant", base_hp=3),
    "night_stalker": MonsterDef("night_stalker", "Night-Stalker", base_hp=3),
}

SPAWN_KEYS = tuple(REGISTRY.keys())


_next_id = 1


def next_id() -> int:
    """Return a stable id for a newly spawned monster."""

    global _next_id
    nid = _next_id
    _next_id += 1
    return nid


def note_existing_id(nid: int) -> None:
    """Advance the internal counter to avoid reusing ``nid``."""

    global _next_id
    if nid >= _next_id:
        _next_id = nid + 1


def spawn(key: str, year: int, x: int, y: int) -> dict:
    """Return default data for a newly spawned monster."""

    counter = next_id()
    return {
        "key": key,
        "name": REGISTRY[key].name,
        "aggro": False,
        "seen": False,
        "id": counter,
        "hp": REGISTRY[key].base_hp,
    }


def resolve_prefix(query: str, names: list[str]) -> str | None:
    q = norm_name(query)
    if not q:
        return None
    matches = [n for n in names if norm_name(n).startswith(q)]
    if len(matches) == 1:
        return matches[0]
    return None


def first_mon_prefix(prefix: str, mons_in_order: list[str]) -> str | None:
    """Return the first monster name matching ``prefix``."""
    p = prefix.strip().lower()
    for name in mons_in_order:
        if name.lower().startswith(p):
            return name
    return None


def describe(key: str) -> str:
    name = REGISTRY[key].name
    return f"It's a {name}."
