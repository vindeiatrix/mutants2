from typing import Iterable, List, MutableMapping, Tuple

from mutants2.ui.theme import red, white

TileKey = Tuple[int, int, int]  # (year, x, y)

MAX_GROUND_ITEMS = 6
MAX_DROPS_PER_DEATH = 6  # includes skull + worn armor


def _room_capacity(world, tile: TileKey) -> int:
    year, x, y = tile
    current = len(world.ground_items(year, x, y))
    return max(0, MAX_GROUND_ITEMS - current)


def _choose_drops(
    monster: MutableMapping[str, object],
    capacity_left: int,
) -> List[MutableMapping[str, object]]:
    """
    Strict order:
      1) inventory items (stored order)
      2) Skull
      3) worn armor
    Obey both MAX_DROPS_PER_DEATH and remaining tile capacity.
    """
    drops: List[MutableMapping[str, object]] = []
    limit = min(MAX_DROPS_PER_DEATH, capacity_left)

    inv: Iterable[MutableMapping[str, object]] = monster.get("inventory", []) or []
    for it in inv:
        if len(drops) >= limit:
            break
        drops.append(it)

    if len(drops) < limit:
        drops.append({"key": "skull", "name": "Skull"})

    worn = monster.get("worn_armor")
    if worn and len(drops) < limit:
        drops.append(worn)

    return drops[:limit]


def _emit_header_lines(slain_name: str, xp: int, riblets: int, ions: int) -> None:
    print(red(f"You have slain {slain_name}!"))
    print(red(f"Your experience points are increased by {xp}!"))
    print(red(f"You collect {riblets} Riblets and {ions} ions from the slain body."))


def _emit_drop_lines(monster_name: str, drops: List[MutableMapping[str, object]]) -> None:
    if not drops:
        print("***")
        return
    for item in drops:
        print("***")
        name = item.get("name") or item.get("key", "Unknown-Item").replace("_", "-").title()
        print(white(f"A {name} is falling from {monster_name}'s body!"))
    print("***")


def _emit_crumble(monster_name: str) -> None:
    print(red(f"{monster_name} is crumbling to dust!"))


def perform_loot_flow(
    world,
    player,
    monster: MutableMapping[str, object],
    tile: TileKey,
    xp: int,
    riblets: int,
    ions: int,
) -> None:
    """
    Call this EXACTLY ONCE whenever a monster dies.
    """
    name = monster.get("name") or monster.get("kind", "Monster-????")

    _emit_header_lines(name, xp, riblets, ions)

    capacity_left = _room_capacity(world, tile)
    drops = _choose_drops(monster, capacity_left)
    _emit_drop_lines(name, drops)

    year, x, y = tile
    for item in drops:
        world.add_ground_item(year, x, y, item)

    _emit_crumble(name)

    # Clear inventory so items aren't duplicated elsewhere
    monster["inventory"] = []
    monster["worn_armor"] = None
