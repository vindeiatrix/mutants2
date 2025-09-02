import random
import datetime
from typing import Dict, Set, Tuple

from .world import Grid, World
from .items import SPAWNABLE_KEYS

WIDTH = 30
HEIGHT = 30
SEED = 42


def generate(width: int = WIDTH, height: int = HEIGHT, seed: int = SEED) -> Grid:
    rand = random.Random(seed)
    adj: Dict[Tuple[int, int], Set[str]] = {(x, y): set() for x in range(width) for y in range(height)}

    def dirs():
        d = [
            ('north', (0, 1), 'south'),
            ('south', (0, -1), 'north'),
            ('east', (1, 0), 'west'),
            ('west', (-1, 0), 'east'),
        ]
        rand.shuffle(d)
        return d

    visited = set()

    def dfs(x: int, y: int) -> None:
        visited.add((x, y))
        for name, (dx, dy), opp in dirs():
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                adj[(x, y)].add(name)
                adj[(nx, ny)].add(opp)
                dfs(nx, ny)

    dfs(0, 0)

    # Carve a small plaza around (0,0)
    fixed_dirs = [
        ('north', (0, 1), 'south'),
        ('south', (0, -1), 'north'),
        ('east', (1, 0), 'west'),
        ('west', (-1, 0), 'east'),
    ]
    for x in range(3):
        for y in range(3):
            for name, (dx, dy), opp in fixed_dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 3 and 0 <= ny < 3:
                    adj[(x, y)].add(name)
                    adj[(nx, ny)].add(opp)

    return Grid(width, height, adj)


def seed_items(world: World, year: int, grid: Grid) -> None:
    """Seed spawnable items on walkable tiles for ``year`` if not already done."""
    if year in world.seeded_years:
        return
    walkable = [(x, y) for x in range(grid.width) for y in range(grid.height) if grid.is_walkable(x, y)]
    rand = random.Random(SEED + year)
    target = round(0.05 * len(walkable))
    if target <= 0:
        world.seeded_years.add(year)
        return
    cells = rand.sample(walkable, min(target, len(walkable)))
    for x, y in cells:
        key = rand.choice(SPAWNABLE_KEYS)
        world.set_ground_item(year, x, y, key)
    world.seeded_years.add(year)


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
