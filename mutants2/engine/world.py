from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Set, Optional, Iterable, Iterator

from .senses import Direction
from . import monsters as monsters_mod, items as items_mod
Coordinate = Tuple[int, int]

ORDER = ("east", "west", "north", "south")
DIRV = {"east": (1, 0), "west": (-1, 0), "north": (0, 1), "south": (0, -1)}


def _dir_from(px: int, py: int, tx: int, ty: int) -> str:
    dx, dy = tx - px, ty - py
    if abs(dx) >= abs(dy):
        return "east" if dx > 0 else "west"
    return "south" if dy > 0 else "north"


@dataclass
class Cell:
    x: int
    y: int


class Grid:
    """A simple 4-neighbour grid."""

    def __init__(self, width: int, height: int, adj: Dict[Coordinate, Set[Direction]]):
        self.width = width
        self.height = height
        self.adj = adj

    def is_walkable(self, x: int, y: int) -> bool:
        return (x, y) in self.adj

    def neighbors(self, x: int, y: int) -> Dict[Direction, Coordinate]:
        dirs = {
            'north': (0, 1),
            'south': (0, -1),
            'east': (1, 0),
            'west': (-1, 0),
        }
        result: Dict[Direction, Coordinate] = {}
        if not self.is_walkable(x, y):
            return result
        for name, (dx, dy) in dirs.items():
            nx, ny = x + dx, y + dy
            if name in self.adj[(x, y)] and 0 <= nx < self.width and 0 <= ny < self.height:
                result[name] = (nx, ny)
        return result


@dataclass
class Year:
    value: int
    grid: Grid


class World:
    def __init__(
        self,
        ground: Optional[Dict[Tuple[int, int, int], list[str] | str]] = None,
        seeded_years: Optional[Set[int]] = None,
        monsters: Optional[Dict[Tuple[int, int, int], dict]] = None,
        *,
        global_seed: int | None = None,
        turn: int = 0,
    ):
        self.years: Dict[int, Year] = {}
        self.ground: Dict[Tuple[int, int, int], list[str]] = {}
        if ground:
            for coord, val in ground.items():
                if isinstance(val, list):
                    self.ground[coord] = list(val)
                else:
                    self.ground[coord] = [val]
        self.seeded_years: Set[int] = set(seeded_years or [])
        self._monsters: Dict[Tuple[int, int, int], dict] = {}
        if monsters:
            for coord, data in monsters.items():
                if isinstance(data, dict):
                    key = data.get("key")
                    hp = data.get("hp")
                    name = data.get("name")
                    aggro = data.get("aggro", False)
                    seen = data.get("seen", False)
                    mid = data.get("id")
                else:
                    key = data
                    hp = None
                    name = None
                    aggro = False
                    seen = False
                    mid = None
                if key is None:
                    continue
                base = monsters_mod.REGISTRY[key].base_hp
                if mid is None:
                    mid = monsters_mod.next_id()
                else:
                    monsters_mod.note_existing_id(int(mid))
                self._monsters[coord] = {
                    "key": key,
                    "hp": int(hp) if hp is not None else base,
                    "name": name or monsters_mod.REGISTRY[key].name,
                    "aggro": bool(aggro),
                    "seen": bool(seen),
                    "id": int(mid),
                }
        if global_seed is None:
            from . import gen

            global_seed = gen.SEED
        self.global_seed = global_seed
        self._recent_monster_moves: list[tuple[int, int, int, int, int]] = []
        self.turn = turn

    def ground_item(self, year: int, x: int, y: int) -> Optional[str]:
        items = self.ground.get((year, x, y))
        if items:
            return items[0]
        return None

    def set_ground_item(self, year: int, x: int, y: int, item_key: Optional[str]) -> None:
        key = (year, x, y)
        if item_key is None:
            self.ground.pop(key, None)
        else:
            self.ground[key] = [item_key]

    def add_ground_item(self, year: int, x: int, y: int, item_key: str) -> None:
        self.ground.setdefault((year, x, y), []).append(item_key)

    def remove_ground_item(self, year: int, x: int, y: int, item_key: str) -> bool:
        items = self.ground.get((year, x, y))
        if not items:
            return False
        try:
            items.remove(item_key)
        except ValueError:
            return False
        if not items:
            self.ground.pop((year, x, y), None)
        return True

    def items_here(self, year: int, x: int, y: int) -> list[str]:
        keys = self.ground.get((year, x, y), [])
        return [items_mod.REGISTRY[k].name for k in keys]

    def items_on_ground(self, year: int, x: int, y: int) -> list[items_mod.ItemDef]:
        keys = self.ground.get((year, x, y), [])
        return [items_mod.REGISTRY[k] for k in keys]

    # Helpers for daily top-up -------------------------------------------------

    def known_years(self) -> list[int]:
        yrs = set(self.years.keys()) | {y for (y, _, _) in self.ground.keys()} | set(self.seeded_years)
        return sorted(yrs)

    def walkable_coords(self, year: int) -> Iterable[Tuple[int, int]]:
        grid = self.year(year).grid
        for x in range(grid.width):
            for y in range(grid.height):
                if grid.is_walkable(x, y):
                    yield (x, y)

    def item_at(self, year: int, x: int, y: int) -> Optional[str]:
        return self.ground_item(year, x, y)

    def place_item(self, year: int, x: int, y: int, item_key: str) -> None:
        self.add_ground_item(year, x, y, item_key)

    def ground_items_count(self, year: int) -> int:
        return sum(len(v) for (yr, _, _), v in self.ground.items() if yr == year)

    @property
    def monsters(self) -> Dict[Tuple[int, int, int], dict]:
        return self._monsters

    # Monsters -----------------------------------------------------------------

    def monsters_in_year(self, year: int) -> dict[tuple[int, int], str]:
        return {
            (x, y): data["key"]
            for (yr, x, y), data in self._monsters.items()
            if yr == year
        }

    def monster_positions(self, year: int) -> Iterator[tuple[int, int, dict]]:
        for (yr, x, y), data in self._monsters.items():
            if yr == year:
                yield (x, y, data)

    def has_monster(self, year: int, x: int, y: int) -> bool:
        return (year, x, y) in self._monsters

    def monster_here(self, year: int, x: int, y: int) -> dict | None:
        return self._monsters.get((year, x, y))

    def monsters_here(self, year: int, x: int, y: int):
        m = self.monster_here(year, x, y)
        if m:
            yield m

    def on_entry_aggro_check(self, year: int, x: int, y: int, player, seed_parts=()) -> list[str]:
        """Mark monsters as seen and run 50/50 aggro rolls on this tile."""

        from .rng import hrand

        yells: list[str] = []
        base = hrand(*seed_parts, year, x, y, "aggro_enter")
        for m in self.monsters_here(year, x, y):
            if not m.get("seen"):
                m["seen"] = True
            if m.get("aggro"):
                continue
            if hrand(base.random(), m.get("id"), "mroll").random() < 0.5:
                m["aggro"] = True
                yells.append(f"{m['name']} yells at you!")
        return yells

    def place_monster(self, year: int, x: int, y: int, key: str) -> bool:
        coord = (year, x, y)
        if coord in self._monsters:
            return False
        self._monsters[coord] = monsters_mod.spawn(key, year, x, y)
        return True

    def ensure_monster(self, year: int, x: int, y: int, key: str) -> None:
        self._monsters[(year, x, y)] = monsters_mod.spawn(key, year, x, y)

    def damage_monster(self, year: int, x: int, y: int, dmg: int) -> bool:
        coord = (year, x, y)
        m = self._monsters.get(coord)
        if not m:
            return False
        m["hp"] = max(0, m["hp"] - max(0, dmg))
        if m["hp"] <= 0:
            self._monsters.pop(coord, None)
            return True
        return False

    def remove_monster(self, year: int, x: int, y: int) -> bool:
        coord = (year, x, y)
        return self._monsters.pop(coord, None) is not None

    def monster_count(self, year: int) -> int:
        return sum(1 for (yr, _, _), _ in self._monsters.items() if yr == year)

    # Movement ---------------------------------------------------------------

    def any_aggro_in_year(self, year: int) -> bool:
        return any(m.get("aggro", False) for _, _, m in self.monster_positions(year))

    def move_monsters_one_tick(self, year: int, player) -> tuple[list[str], tuple[str, str] | None]:
        """Advance ONLY aggro'd monsters one step each.

        Returns arrival messages for monsters entering the player's tile and a
        footsteps event of the form ``("faint"|"loud", dir)`` or ``None`` if no
        monster movement produced audible footsteps.
        """

        if not self.any_aggro_in_year(year):
            return [], None

        arrivals: list[str] = []
        footsteps_event: tuple[str, str] | None = None

        px, py = player.x, player.y

        # Build occupancy map of monster locations (player tile allowed)
        occ = {(x, y) for (x, y, _) in self.monster_positions(year)}

        for (x, y, m) in list(self.monster_positions(year)):
            if not m.get("aggro", False):
                continue  # passive monsters never move

            base_d = abs(px - x) + abs(py - y)

            best: tuple[str, int, int, int] | None = None
            for d in ORDER:
                if not self.is_open(year, x, y, d):
                    continue
                nx, ny = x + DIRV[d][0], y + DIRV[d][1]
                if (nx, ny) in occ:
                    continue
                new_d = abs(px - nx) + abs(py - ny)
                if new_d < base_d:
                    cand = (d, nx, ny, new_d)
                    if (
                        best is None
                        or cand[3] < best[3]
                        or (cand[3] == best[3] and ORDER.index(d) < ORDER.index(best[0]))
                    ):
                        best = cand

            if best is None:
                continue  # no progress toward player

            d, nx, ny, _ = best

            # Commit move
            del self._monsters[(year, x, y)]
            self._monsters[(year, nx, ny)] = m
            occ.remove((x, y))
            occ.add((nx, ny))

            if (nx, ny) == (px, py):
                arrivals.append(f"{m['name']} has just arrived from the {d}.")

            if footsteps_event is None:
                dist = abs(px - nx) + abs(py - ny)
                if 3 <= dist <= 6:
                    footsteps_event = ("faint", _dir_from(px, py, nx, ny))
                elif dist == 2:
                    footsteps_event = ("loud", _dir_from(px, py, nx, ny))

        return arrivals, footsteps_event

    def shadow_dirs(self, year: int, x: int, y: int) -> list[str]:
        dirs: list[str] = []
        for d in ORDER:
            if self.is_open(year, x, y, d):
                nx, ny = x + DIRV[d][0], y + DIRV[d][1]
                if self.has_monster(year, nx, ny):
                    dirs.append(d)
        return dirs

    def adjacent_monster_names(self, year: int, x: int, y: int) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        for d in ("east", "west", "north", "south"):
            if self.is_open(year, x, y, d):
                ax, ay = self.step(x, y, d)
                m = self.monster_here(year, ax, ay)
                if m:
                    key = m["key"]
                    name = monsters_mod.REGISTRY[key].name
                    results.append((name, key))
        return results

    def resolve_monster_prefix_nearby(self, year: int, x: int, y: int, query: str) -> str | None:
        candidates: list[str] = []
        name_to_key: dict[str, str] = {}
        here = self.monster_here(year, x, y)
        if here:
            key = here["key"]
            name = monsters_mod.REGISTRY[key].name
            candidates.append(name)
            name_to_key[name] = key
        for name, key in self.adjacent_monster_names(year, x, y):
            candidates.append(name)
            name_to_key[name] = key
        match = monsters_mod.resolve_prefix(query, candidates)
        if match:
            return name_to_key[match]
        return None

    def monsters_moved_near(self, year: int, x: int, y: int, radius: int = 4) -> bool:
        hit = False
        for yr, x0, y0, x1, y1 in self._recent_monster_moves:
            if yr != year:
                continue
            if abs(x0 - x) + abs(y0 - y) <= radius or abs(x1 - x) + abs(y1 - y) <= radius:
                hit = True
                break
        self._recent_monster_moves.clear()
        return hit

    def force_monster_move_within4(self, year: int = 2000) -> None:
        self._recent_monster_moves.append((year, 1, 0, 1, 1))

    _DIRS: dict[Direction, tuple[int, int]] = {
        "north": (0, 1),
        "south": (0, -1),
        "east": (1, 0),
        "west": (-1, 0),
    }

    def is_open(self, year: int, x: int, y: int, direction: Direction) -> bool:
        """Return ``True`` if an open passage exists from ``(x, y)`` to ``direction``."""
        grid = self.year(year).grid
        return direction in grid.neighbors(x, y)

    def step(self, x: int, y: int, direction: Direction) -> tuple[int, int]:
        """Return coordinates stepped one tile in ``direction`` from ``(x, y)``."""
        dx, dy = self._DIRS[direction]
        return x + dx, y + dy

    def nearest_monster(
        self, year: int, x: int, y: int, max_dist: int = 4
    ) -> tuple[int, int, int] | None:
        hit: tuple[int, int, int] | None = None
        for (yr, mx, my), _data in self._monsters.items():
            if yr != year:
                continue
            dist = abs(mx - x) + abs(my - y)
            if dist > max_dist:
                continue
            if hit is None or dist < hit[2]:
                hit = (mx - x, my - y, dist)
        return hit

    def year(self, value: int) -> Year:
        """Return the :class:`Year` for ``value`` generating it if needed."""
        if value not in self.years:
            from . import gen

            grid = gen.generate(seed=value)
            # Ensure starting location is always open
            if not grid.is_walkable(0, 0):
                raise ValueError("start tile (0,0) must be open")
            self.years[value] = Year(value, grid)
            gen.seed_items(self, value, grid)
            had_start = self.has_monster(value, 0, 0)
            gen.seed_monsters_for_year(self, value, self.global_seed)
            # Ensure starting tile is clear unless a monster was explicitly placed
            if not had_start:
                self.remove_monster(value, 0, 0)
        return self.years[value]
