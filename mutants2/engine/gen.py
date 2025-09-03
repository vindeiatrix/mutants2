import random
import datetime
from typing import Dict, Set, Tuple

from .world import Grid, World, GRID_MIN, GRID_MAX
from .items import SPAWNABLE_KEYS
from .monsters import SPAWN_KEYS

WIDTH = GRID_MAX - GRID_MIN
HEIGHT = GRID_MAX - GRID_MIN
SEED = 42


def generate(width: int = WIDTH, height: int = HEIGHT, seed: int = SEED) -> Grid:
    """Return a fully open grid with the canonical bounds."""
    return Grid(width, height)


def seed_items(world: World, year: int, grid: Grid) -> None:
    """Seed spawnable items on walkable tiles for ``year`` if not already done."""
    if year in world.seeded_years:
        return
    walkable = list(world.walkable_coords(year))
    rand = random.Random(SEED + year)
    rate = 0.05 * 5.0
    target = min(round(0.5 * len(walkable)), round(rate * len(walkable)))
    if target <= 0:
        world.seeded_years.add(year)
        return
    cells = rand.choices(walkable, k=target)
    for x, y in cells:
        key = rand.choice(SPAWNABLE_KEYS)
        world.add_ground_item(year, x, y, key)
    world.seeded_years.add(year)


def seed_monsters_for_year(world: World, year: int, global_seed: int) -> None:
    walkables = list(world.walkable_coords(year))
    if not walkables:
        return
    import random

    rng = random.Random(hash((global_seed, year, "monsters_v1")))
    rate = 0.06 * 3.0
    target = min(round(0.35 * len(walkables)), max(0, round(rate * len(walkables))))
    rng.shuffle(walkables)
    placed = 0
    for (x, y) in walkables:
        if world.item_at(year, x, y) is None:
            world.place_monster(year, x, y, SPAWN_KEYS[0])
            placed += 1
            if placed >= target:
                break


# Daily top-up ----------------------------------------------------------------

def _today_from_env_or_system(fake_today: str | None) -> datetime.date:
    if fake_today:
        return datetime.date.fromisoformat(fake_today)
    return datetime.date.today()


def _rng_for_day(global_seed: int, year: int, day: datetime.date) -> random.Random:
    seed = hash((global_seed, year, int(day.strftime("%Y%m%d")), "topup"))
    return random.Random(seed)


def count_walkable(world: World, year: int) -> int:
    return sum(1 for _ in world.walkable_coords(year))


def ground_count(world: World, year: int) -> int:
    return world.ground_items_count(year)


def _empty_walkables(world: World, year: int) -> list[Tuple[int, int]]:
    return [(x, y) for (x, y) in world.walkable_coords(year) if world.item_at(year, x, y) is None]


def daily_topup_year(world: World, year: int, global_seed: int, day: datetime.date) -> int:
    """Top up a single year to ~5% target; returns number of items placed."""
    walkables = count_walkable(world, year)
    target = max(0, round(0.05 * walkables))
    have = ground_count(world, year)
    need = max(0, target - have)
    if need == 0:
        return 0

    rng = _rng_for_day(global_seed, year, day)
    empties = _empty_walkables(world, year)
    if not empties:
        return 0

    rng.shuffle(empties)
    placed = 0
    for (x, y) in empties[:need]:
        item_key = rng.choice(SPAWNABLE_KEYS)
        world.place_item(year, x, y, item_key)
        placed += 1
    return placed


def daily_topup_if_needed(world: World, player, save, *, fake_today: str | None = None) -> int:
    today = _today_from_env_or_system(fake_today or getattr(save, "fake_today_override", None))
    if getattr(save, "last_topup_date", None) == today.isoformat():
        return 0

    total = 0
    for yr in world.known_years():
        total += daily_topup_year(world, yr, save.global_seed, today)

    save.last_topup_date = today.isoformat()
    return total
