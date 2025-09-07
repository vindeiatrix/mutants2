from __future__ import annotations
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, MutableMapping, Sequence

from mutants2.types import ItemInstance
from .items_util import coerce_item
from .items import norm_name


@dataclass(frozen=True)
class MonsterDef:
    key: str
    name: str
    level: int
    strength: int
    intelligence: int
    wisdom: int
    dexterity: int
    constitution: int
    charisma: int
    weapon: ItemInstance
    armor: ItemInstance
    base_hp: int = 3


REGISTRY: dict[str, MonsterDef] = {
    "rust-knight": MonsterDef(
        "rust-knight",
        "Rust-Knight",
        7,
        60,
        20,
        18,
        40,
        55,
        15,
        {"key": "iron-sabre", "enchant": 1, "base_power": 8},
        {"key": "plate-jacket", "enchant": 1, "ac_bonus": 10},
    ),
    "plasma-bandit": MonsterDef(
        "plasma-bandit",
        "Plasma-Bandit",
        9,
        70,
        22,
        24,
        50,
        60,
        18,
        {"key": "plasma-knife", "enchant": 1, "base_power": 9},
        {"key": "woven-plasmacoat", "enchant": 1, "ac_bonus": 11},
    ),
    "chrono-magus": MonsterDef(
        "chrono-magus",
        "Chrono-Magus",
        11,
        65,
        90,
        95,
        55,
        58,
        40,
        {"key": "time-rod", "enchant": 1, "base_power": 8},
        {"key": "chrono-robes", "enchant": 1, "ac_bonus": 10},
    ),
    "ion-wraith": MonsterDef(
        "ion-wraith",
        "Ion-Wraith",
        13,
        80,
        60,
        60,
        60,
        70,
        25,
        {"key": "ion-talons", "enchant": 1, "base_power": 10},
        {"key": "phase-carapace", "enchant": 1, "ac_bonus": 12},
    ),
    "singularity-brute": MonsterDef(
        "singularity-brute",
        "Singularity-Brute",
        15,
        90,
        30,
        30,
        65,
        85,
        20,
        {"key": "gravity-hammer", "enchant": 1, "base_power": 12},
        {"key": "mass-plate", "enchant": 1, "ac_bonus": 13},
    ),
}
# Legacy aliases for backward compatibility in tests
REGISTRY.update({
    "mutant": REGISTRY["rust-knight"],
    "night_stalker": REGISTRY["rust-knight"],
    "dragon_turtle": REGISTRY["rust-knight"],
    "glabrezu_demon": REGISTRY["rust-knight"],
    "leucrotta": REGISTRY["rust-knight"],
    "lizard_man": REGISTRY["rust-knight"],
    "evil_pegasus": REGISTRY["rust-knight"],
    "sandworm": REGISTRY["rust-knight"],
    "umber_hulk": REGISTRY["rust-knight"],
    "gargoyle": REGISTRY["rust-knight"],
    "kraken": REGISTRY["rust-knight"],
    "opal_cockatrice": REGISTRY["rust-knight"],
})

SPAWN_KEYS = (
    "rust-knight",
    "plasma-bandit",
    "chrono-magus",
    "ion-wraith",
    "singularity-brute",
)


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


def spawn(key: str, mid: int) -> MutableMapping[str, object]:
    """Return default data for a newly spawned monster."""

    d = REGISTRY[key]
    name = f"{d.name}-{mid:04d}"
    weapon = coerce_item(d.weapon)
    armor = coerce_item(d.armor)
    ac_total = armor.get("ac_bonus", 0) + d.dexterity // 10
    return {
        "key": key,
        "name": name,
        "aggro": False,
        "seen": False,
        "has_yelled_this_aggro": False,
        "id": mid,
        "hp": d.base_hp,
        "loot_ions": 0,
        "loot_riblets": 0,
        "level": d.level,
        "strength": d.strength,
        "intelligence": d.intelligence,
        "wisdom": d.wisdom,
        "dexterity": d.dexterity,
        "constitution": d.constitution,
        "charisma": d.charisma,
        "wielded_weapon": weapon,
        "worn_armor": armor,
        "ac_total": ac_total,
    }


def resolve_prefix(query: str, names: Sequence[str]) -> str | None:
    q = norm_name(query)
    if not q:
        return None
    matches = [n for n in names if norm_name(n).startswith(q)]
    if len(matches) == 1:
        return matches[0]
    return None


def first_mon_prefix(prefix: str, mons_in_order: Sequence[str]) -> str | None:
    p = prefix.strip().lower()
    for name in mons_in_order:
        if name.lower().startswith(p):
            return name
    return None


def describe(key: str) -> str:
    name = REGISTRY[key].name
    return f"It's a {name}."


def seed_monsters(world) -> None:
    import random

    world.monsters.clear()
    plan: Mapping[int, list[str]] = {
        2000: ["rust-knight"] * 20,
        2100: ["plasma-bandit"] * 10 + ["chrono-magus"] * 10,
        2200: ["ion-wraith"] * 10 + ["singularity-brute"] * 10,
    }
    for year, keys in plan.items():
        coords = [
            (x, y)
            for (x, y) in world.walkable_coords(year)
            if abs(x) > 2 or abs(y) > 2
        ]
        rng = random.Random(hash((world.global_seed, year, "seed_monsters_v1")))
        rng.shuffle(coords)
        for (x, y), key in zip(coords, keys):
            world.place_monster(year, x, y, key)

