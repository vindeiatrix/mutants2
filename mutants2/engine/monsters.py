from dataclasses import dataclass


@dataclass(frozen=True)
class MonsterDef:
    key: str
    name: str
    base_hp: int = 3  # small, so combat resolves quickly


REGISTRY = {
    "mutant": MonsterDef("mutant", "Mutant", base_hp=3),
}

SPAWN_KEYS = tuple(REGISTRY.keys())
