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
    "dragon_turtle": MonsterDef("dragon_turtle", "Dragon-Turtle", base_hp=3),
    "glabrezu_demon": MonsterDef("glabrezu_demon", "Glabrezu-Demon", base_hp=3),
    "leucrotta": MonsterDef("leucrotta", "Leucrotta", base_hp=3),
    "lizard_man": MonsterDef("lizard_man", "Lizard-Man", base_hp=3),
    "evil_pegasus": MonsterDef("evil_pegasus", "Evil-Pegasus", base_hp=3),
    "sandworm": MonsterDef("sandworm", "Sandworm", base_hp=3),
    "umber_hulk": MonsterDef("umber_hulk", "Umber-Hulk", base_hp=3),
    "gargoyle": MonsterDef("gargoyle", "Gargoyle", base_hp=3),
    "kraken": MonsterDef("kraken", "Kraken", base_hp=3),
    "opal_cockatrice": MonsterDef("opal_cockatrice", "Opal-Cockatrice", base_hp=3),
}

SPAWN_KEYS = tuple(REGISTRY.keys())


class MonsterIdAllocator:
    """Allocate unique 4-digit monster ids."""

    def __init__(self, rng):
        self._free = list(range(1000, 10000))
        rng.shuffle(self._free)

    def allocate(self) -> int:
        return self._free.pop()

    def release(self, mid: int) -> None:
        if 1000 <= mid <= 9999 and mid not in self._free:
            self._free.append(mid)

    def note_existing(self, mid: int) -> None:
        try:
            self._free.remove(mid)
        except ValueError:
            pass


def spawn(key: str, mid: int) -> dict:
    """Return default data for a newly spawned monster."""

    name = f"{REGISTRY[key].name}-{mid:04d}"
    return {
        "key": key,
        "name": name,
        "aggro": False,
        "seen": False,
        "yelled_once": False,
        "id": mid,
        "hp": REGISTRY[key].base_hp,
        "loot_ions": 0,
        "loot_riblets": 0,
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
