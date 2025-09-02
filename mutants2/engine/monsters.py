from dataclasses import dataclass


from .items import norm_name

@dataclass(frozen=True)
class MonsterDef:
    key: str
    name: str
    base_hp: int = 3  # small, so combat resolves quickly


REGISTRY = {
    "mutant": MonsterDef("mutant", "Mutant", base_hp=3),
}

SPAWN_KEYS = tuple(REGISTRY.keys())


def resolve_prefix(query: str, names: list[str]) -> str | None:
    q = norm_name(query)
    if not q:
        return None
    matches = [n for n in names if norm_name(n).startswith(q)]
    if len(matches) == 1:
        return matches[0]
    return None


def describe(key: str) -> str:
    name = REGISTRY[key].name
    return f"It's a {name}."
