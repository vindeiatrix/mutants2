import random
import datetime
from typing import Tuple

from .world import Grid, World, GRID_MIN, GRID_MAX
from .items import SPAWNABLE_KEYS
from .monsters import SPAWN_KEYS

WIDTH = GRID_MAX - GRID_MIN
HEIGHT = GRID_MAX - GRID_MIN
SEED = 42

# ---------------------------------------------------------------------------
# Item seeding / density helpers
# ---------------------------------------------------------------------------

ITEM_TARGET_MEAN = 400
ITEM_TARGET_SPREAD = 0.10  # ±10%


def _item_target(global_seed: int, year: int) -> int:
    """Return the deterministic item target for ``year``.

    The target is sampled once per year using a RNG derived from the world's
    global seed and the year number.  This ensures that both seeding and debug
    top-ups converge on the same per-year target.
    """

    rng = random.Random(hash((global_seed, year, "item_target_v1")))
    lo = int(ITEM_TARGET_MEAN * (1 - ITEM_TARGET_SPREAD))
    hi = int(ITEM_TARGET_MEAN * (1 + ITEM_TARGET_SPREAD))
    return rng.randint(lo, hi)


def _rng_for_year(global_seed: int, year: int, tag: str) -> random.Random:
    return random.Random(hash((global_seed, year, tag)))


def _topup_to_target(world: World, year: int, target: int, rng: random.Random) -> int:
    """Ensure ``year`` contains exactly ``target`` items.

    Returns the number of items placed.  Item placement prefers empty walkable
    cells and selects uniformly from the spawnable registry.
    """

    have = world.ground_items_count(year)
    need = max(0, target - have)
    if need <= 0:
        return 0

    walkables = [
        (x, y)
        for (x, y) in world.walkable_coords(year)
        if world.item_at(year, x, y) is None
    ]
    if not walkables:
        return 0
    rng.shuffle(walkables)
    placed = 0
    for x, y in walkables:
        item_key = rng.choice(SPAWNABLE_KEYS)
        world.place_item(year, x, y, item_key)
        placed += 1
        if placed >= need:
            break
    return placed


def debug_item_topup(world: World, year: int, global_seed: int) -> tuple[int, int, int]:
    """Top up ``year`` to its deterministic target for debug commands.

    Returns a tuple ``(before, after, target)`` describing the item counts
    before and after placement and the target used.
    """

    target = _item_target(global_seed, year)
    before = world.ground_items_count(year)
    rng = _rng_for_year(global_seed, year, "debug_item_topup_v1")
    _topup_to_target(world, year, target, rng)
    after = world.ground_items_count(year)
    return before, after, target


def generate(width: int = WIDTH, height: int = HEIGHT, seed: int = SEED) -> Grid:
    """Return a fully open grid with the canonical bounds."""
    return Grid(width, height)


def seed_items(world: World, year: int, grid: Grid) -> None:
    """Seed spawnable items on walkable tiles for ``year`` if not already done."""
    if year in world.seeded_years:
        return
    target = _item_target(world.global_seed, year)
    rng = _rng_for_year(world.global_seed, year, "seed_items_v1")
    _topup_to_target(world, year, target, rng)
    world.seeded_years.add(year)


def seed_monsters_for_year(world: World, year: int, global_seed: int) -> None:
    walkables = list(world.walkable_coords(year))
    if not walkables:
        return
    import random

    rng = random.Random(hash((global_seed, year, "monsters_v1")))
    target = _monster_target(world, year)
    rng.shuffle(walkables)
    placed = 0
    for x, y in walkables:
        if world.item_at(year, x, y) is None:
            world.place_monster(year, x, y, SPAWN_KEYS[0])
            placed += 1
            if placed >= target:
                break


def _monster_target(world: World, year: int) -> int:
    walkables = list(world.walkable_coords(year))
    if not walkables:
        return 0
    rate = 0.06 * 0.5
    return min(round(0.35 * len(walkables)), max(0, round(rate * len(walkables))))


def debug_monster_topup(
    world: World, year: int, global_seed: int
) -> tuple[int, int, int]:
    """Top up monsters in ``year`` to the baseline target.

    Returns ``(before, after, target)``.
    """

    target = _monster_target(world, year)
    before = world.monster_count(year)
    need = max(0, target - before)
    if need <= 0:
        return before, before, target
    walkables = [
        (x, y)
        for (x, y) in world.walkable_coords(year)
        if world.item_at(year, x, y) is None and not world.has_monster(year, x, y)
    ]
    rng = _rng_for_year(global_seed, year, "debug_mon_topup_v1")
    rng.shuffle(walkables)
    placed = 0
    for x, y in walkables:
        world.place_monster(year, x, y, SPAWN_KEYS[0])
        placed += 1
        if placed >= need:
            break
    after = world.monster_count(year)
    return before, after, target


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
    return [
        (x, y)
        for (x, y) in world.walkable_coords(year)
        if world.item_at(year, x, y) is None
    ]


def daily_topup_year(
    world: World, year: int, global_seed: int, day: datetime.date
) -> int:
    """Top up a single year to its deterministic target."""
    target = _item_target(global_seed, year)
    rng = _rng_for_day(global_seed, year, day)
    return _topup_to_target(world, year, target, rng)


def daily_topup_if_needed(
    world: World, player, save, *, fake_today: str | None = None
) -> int:
    today = _today_from_env_or_system(
        fake_today or getattr(save, "fake_today_override", None)
    )
    if getattr(save, "last_topup_date", None) == today.isoformat():
        return 0

    total = 0
    for yr in world.known_years():
        total += daily_topup_year(world, yr, save.global_seed, today)

    save.last_topup_date = today.isoformat()
    return total
