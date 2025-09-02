from dataclasses import dataclass


@dataclass(frozen=True)
class MonsterDef:
    key: str
    name: str


REGISTRY = {
    "mutant": MonsterDef("mutant", "Mutant"),
}

SPAWN_KEYS = tuple(REGISTRY.keys())
