from __future__ import annotations

import random
from dataclasses import dataclass
from typing import (
    Dict,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    Tuple,
    cast,
)

from .types import (
    Direction,
    MonsterList,
    MonsterRec,
)
from .types import ItemInstance, TileKey
from .items_util import coerce_item
from .items_resolver import get_item_def_by_key
from ..ui.items_render import display_item_name_plain
from . import monsters as monsters_mod, items as items_mod, rng as rng_mod
from .ai import set_aggro
from ..data.room_headers import ROOM_HEADERS

Coordinate = Tuple[int, int]

# ---------------------------------------------------------------------------
# Grid topology helpers
# ---------------------------------------------------------------------------

GRID_MIN = -15
GRID_MAX = 15
# Centuries the player can travel between.  Each century has an independent
# world state and uses the same generation parameters as the others.
ALLOWED_CENTURIES = [
    2000,
    2100,
    2200,
    2300,
    2400,
    2500,
    2600,
    2700,
    2800,
    2900,
    3000,
]
LOWEST_CENTURY, HIGHEST_CENTURY = 2000, 3000


def in_bounds(x: int, y: int) -> bool:
    return GRID_MIN <= x < GRID_MAX and GRID_MIN <= y < GRID_MAX


DIR: Mapping[Direction, Tuple[int, int]] = {
    "east": (1, 0),
    "west": (-1, 0),
    "north": (0, 1),
    "south": (0, -1),
}

ORDER: tuple[Direction, ...] = ("east", "west", "north", "south")


def step(x: int, y: int, d: Direction) -> tuple[int, int]:
    dx, dy = DIR[d]
    return x + dx, y + dy


def _dir_from(px: int, py: int, tx: int, ty: int) -> Direction:
    dx, dy = tx - px, ty - py
    if abs(dx) >= abs(dy):
        return "east" if dx > 0 else "west"
    return "north" if dy > 0 else "south"


def footstep_direction(dx: int, dy: int) -> str:
    sx = (dx > 0) - (dx < 0)
    sy = (dy > 0) - (dy < 0)
    if sx == 0 and sy == 0:
        return ""
    if sx == 0:
        return "north" if sy > 0 else "south"
    if sy == 0:
        return "east" if sx > 0 else "west"
    hor = "east" if sx > 0 else "west"
    ver = "north" if sy > 0 else "south"
    return f"{ver}-{hor}"


@dataclass
class Cell:
    x: int
    y: int


class Grid:
    """A simple 4-neighbour grid with fully open connectivity."""

    def __init__(
        self, width: int = GRID_MAX - GRID_MIN, height: int = GRID_MAX - GRID_MIN
    ):
        self.width = width
        self.height = height

    def is_walkable(self, x: int, y: int) -> bool:
        return in_bounds(x, y)

    def neighbors(self, x: int, y: int) -> Mapping[Direction, Coordinate]:
        result: dict[Direction, Coordinate] = {}
        if not self.is_walkable(x, y):
            return result
        for name, (dx, dy) in DIR.items():
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                result[name] = (nx, ny)
        return result


@dataclass
class Year:
    value: int
    grid: Grid


GroundMap = Mapping[TileKey, Iterable[ItemInstance]]


class World:
    def __init__(
        self,
        ground: GroundMap | None = None,
        seeded_years: Optional[Set[int]] = None,
        monsters: Mapping[TileKey, MonsterList] | None = None,
        *,
        seed_monsters: bool = False,
        global_seed: int | None = None,
        turn: int = 0,
    ):
        self.years: Dict[int, Year] = {}
        self.ground: MutableMapping[TileKey, list[ItemInstance]] = {}
        if ground:
            for coord, val in ground.items():
                self.ground[coord] = [coerce_item(v) for v in val]
        self.seeded_years: Set[int] = set(seeded_years or [])
        if global_seed is None:
            from . import gen

            global_seed = gen.SEED
        self.global_seed = global_seed
        self._id_alloc = monsters_mod.MonsterIdAllocator(
            rng_mod.hrand(self.global_seed, "mon_ids_v1")
        )
        self._monsters: MutableMapping[TileKey, list[MonsterRec]] = {}
        self._seed_monsters = seed_monsters
        if monsters:
            for coord, data in monsters.items():
                lst: list[MonsterRec] = []
                for entry in data:
                    key_val = entry.get("key")
                    if key_val is None:
                        continue
                    m_key = cast(str, key_val)
                    hp_val = entry.get("hp")
                    hp_int = int(cast(int, hp_val)) if hp_val is not None else None
                    aggro = entry.get("aggro", False)
                    seen = entry.get("seen", False)
                    has_yelled = entry.get("yelled_once") or entry.get(
                        "has_yelled_this_aggro", False
                    )
                    mid_val = entry.get("id")
                    mid = int(cast(int, mid_val)) if mid_val is not None else None
                    loot_i = entry.get("loot_ions", 0)
                    loot_r = entry.get("loot_riblets", 0)
                    base = monsters_mod.REGISTRY[m_key].base_hp
                    if mid is None:
                        mid = self._id_alloc.allocate()
                    else:
                        self._id_alloc.note_existing(mid)
                    name = f"{monsters_mod.REGISTRY[m_key].name}-{mid:04d}"
                    m: MutableMapping[str, object] = {
                        "key": m_key,
                        "hp": hp_int if hp_int is not None else base,
                        "name": name,
                        "aggro": bool(aggro),
                        "seen": bool(seen),
                        "yelled_once": bool(has_yelled),
                        "id": int(mid),
                        "loot_ions": int(cast(int, loot_i)),
                        "loot_riblets": int(cast(int, loot_r)),
                    }
                    if m.get("aggro") and not m.get("seen"):
                        m["aggro"] = False
                        m["yelled_once"] = False
                    lst.append(m)
                if lst:
                    self._monsters[coord] = lst
        self._recent_monster_moves: list[tuple[int, int, int, int, int]] = []
        self.turn = turn
        self._room_headers: Dict[Tuple[int, int, int], str] = {}

    def ground_item(self, year: int, x: int, y: int) -> Optional[ItemInstance]:
        items = self.ground.get((year, x, y))
        if items:
            return items[0]
        return None

    def ground_items(self, year: int, x: int, y: int) -> list[ItemInstance]:
        """Return all ground items at the given tile."""
        return self.ground.get((year, x, y), [])

    def set_ground_item(
        self, year: int, x: int, y: int, item_key: Optional[str]
    ) -> None:
        key = (year, x, y)
        if item_key is None:
            self.ground.pop(key, None)
        else:
            self.ground[key] = [coerce_item(item_key)]

    def add_ground_item(
        self, year: int, x: int, y: int, item: ItemInstance | str
    ) -> None:
        self.ground.setdefault((year, x, y), []).append(coerce_item(item))

    def remove_ground_item(
        self, year: int, x: int, y: int, item_key: str
    ) -> ItemInstance | None:
        items = self.ground.get((year, x, y))
        if not items:
            return None
        for i, inst in enumerate(items):
            if inst["key"] == item_key:
                removed = items.pop(i)
                if not items:
                    self.ground.pop((year, x, y), None)
                return removed
        return None

    def items_here(self, year: int, x: int, y: int) -> list[str]:
        vals = self.ground.get((year, x, y), [])
        names: list[str] = []
        for v in vals:
            idef = get_item_def_by_key(v["key"])
            names.append(display_item_name_plain(v, idef))
        return names

    def items_on_ground(self, year: int, x: int, y: int) -> list[items_mod.ItemDef]:
        vals = self.ground.get((year, x, y), [])
        out: list[items_mod.ItemDef] = []
        for v in vals:
            idef = get_item_def_by_key(v["key"])
            if idef:
                out.append(idef)
        return out

    def room_description(self, year: int, x: int, y: int) -> str:
        """Return the room header for the given tile, generating on demand."""
        key = (year, x, y)
        header = self._room_headers.get(key)
        if header is None:
            rng = random.Random(hash((self.global_seed, year, x, y, "room_header_v1")))
            header = rng.choice(ROOM_HEADERS)
            self._room_headers[key] = header
        return header

    # Helpers for daily top-up -------------------------------------------------

    def known_years(self) -> list[int]:
        yrs = (
            set(self.years.keys())
            | {y for (y, _, _) in self.ground.keys()}
            | set(self.seeded_years)
        )
        return sorted(yrs)

    def walkable_coords(self, year: int) -> Iterable[Tuple[int, int]]:
        for y in range(GRID_MIN, GRID_MAX):
            for x in range(GRID_MIN, GRID_MAX):
                yield (x, y)

    def item_at(self, year: int, x: int, y: int) -> ItemInstance | None:
        return self.ground_item(year, x, y)

    def place_item(self, year: int, x: int, y: int, item_key: str) -> None:
        self.add_ground_item(year, x, y, item_key)

    def ground_items_count(self, year: int) -> int:
        return sum(len(v) for (yr, _, _), v in self.ground.items() if yr == year)

    # convenience aliases used in tests
    def count_monsters_for_year(self, year: int) -> int:
        return self.monster_count(year)

    def count_items_for_year(self, year: int) -> int:
        return self.ground_items_count(year)

    @property
    def monsters(self) -> MutableMapping[TileKey, list[MonsterRec]]:
        return self._monsters

    # Monsters -----------------------------------------------------------------

    def monsters_in_year(self, year: int) -> dict[tuple[int, int], list[str]]:
        out: dict[tuple[int, int], list[str]] = {}
        for (yr, x, y), lst in self._monsters.items():
            if yr == year:
                out[(x, y)] = [cast(str, m["key"]) for m in lst]
        return out

    def monster_positions(self, year: int) -> Iterator[tuple[int, int, MonsterRec]]:
        for (yr, x, y), lst in self._monsters.items():
            if yr == year:
                for m in lst:
                    yield (x, y, m)

    def has_monster(self, year: int, x: int, y: int) -> bool:
        return bool(self._monsters.get((year, x, y)))

    def monster_here(self, year: int, x: int, y: int) -> MonsterRec | None:
        lst = self._monsters.get((year, x, y))
        return lst[0] if lst else None

    def monsters_here(self, year: int, x: int, y: int) -> list[MonsterRec]:
        return list(self._monsters.get((year, x, y), []))

    def on_entry_aggro_check(
        self, year: int, x: int, y: int, player, seed_parts=()
    ) -> list[str]:
        """Mark monsters as seen and run 50/50 aggro rolls on this tile."""

        from .rng import hrand

        yells: list[str] = []
        base = hrand(*seed_parts, year, x, y, "aggro_enter")
        for m in self.monsters_here(year, x, y):
            mm = cast(MutableMapping[str, object], m)
            if not mm.get("seen"):
                mm["seen"] = True
            if mm.get("aggro"):
                continue
            if hrand(base.random(), mm.get("id"), "mroll").random() < 0.5:
                msg = set_aggro(mm)
                if msg:
                    yells.append(msg)
        return yells

    def reset_all_aggro(self) -> None:
        for lst in self._monsters.values():
            for m in lst:
                mm = cast(MutableMapping[str, object], m)
                mm["aggro"] = False
                mm["yelled_once"] = False

    def reset_aggro_in_year(self, year: int) -> None:
        for _, _, m in self.monster_positions(year):
            mm = cast(MutableMapping[str, object], m)
            mm["aggro"] = False
            mm["yelled_once"] = False

    def place_monster(self, year: int, x: int, y: int, key: str) -> bool:
        coord = (year, x, y)
        mid = self._id_alloc.allocate()
        self._monsters.setdefault(coord, []).append(monsters_mod.spawn(key, mid))
        return True

    def ensure_monster(self, year: int, x: int, y: int, key: str) -> None:
        mid = self._id_alloc.allocate()
        self._monsters.setdefault((year, x, y), []).append(monsters_mod.spawn(key, mid))

    def damage_monster(self, year: int, x: int, y: int, dmg: int, player=None) -> bool:
        coord = (year, x, y)
        lst = self._monsters.get(coord)
        if not lst:
            return False
        m = cast(MutableMapping[str, object], lst[0])
        mid = int(cast(int, m["id"]))
        hp_val = int(cast(int, m["hp"]))
        m["hp"] = max(0, hp_val - max(0, dmg))
        if int(cast(int, m["hp"])) <= 0:
            lst.pop(0)
            self._id_alloc.release(mid)
            if not lst:
                self._monsters.pop(coord, None)
            if player is not None and getattr(
                player, "ready_to_combat_id", None
            ) == str(mid):
                player.ready_to_combat_id = None
                player.ready_to_combat_name = None
            return True
        return False

    def remove_monster(self, year: int, x: int, y: int, player=None) -> bool:
        coord = (year, x, y)
        lst = self._monsters.get(coord)
        if not lst:
            return False
        m = lst.pop(0)
        mid = int(cast(int, m.get("id", 0)))
        self._id_alloc.release(mid)
        if not lst:
            self._monsters.pop(coord, None)
        if player is not None and getattr(player, "ready_to_combat_id", None) == str(
            mid
        ):
            player.ready_to_combat_id = None
            player.ready_to_combat_name = None
        return True

    def monster_count(self, year: int) -> int:
        return sum(len(v) for (yr, _, _), v in self._monsters.items() if yr == year)

    # Movement ---------------------------------------------------------------

    def any_aggro_in_year(self, year: int) -> bool:
        return any(m.get("aggro", False) for _, _, m in self.monster_positions(year))

    def move_monsters_one_tick(
        self, year: int, player
    ) -> tuple[list[tuple[int, str, Direction]], tuple[str, str] | None]:
        """Advance ONLY aggro'd monsters one step each.

        Returns arrival info for monsters entering the player's tile as a list
        of ``(id, name, direction)`` and a footsteps event of the form
        ``("faint"|"loud", dir)`` or ``None`` if no monster movement produced
        audible footsteps.
        """

        if not self.any_aggro_in_year(year):
            return [], None

        arrivals: list[tuple[int, str, Direction]] = []
        footsteps_event: tuple[str, str] | None = None

        px, py = player.x, player.y

        for x, y, m in list(self.monster_positions(year)):
            if not m.get("aggro", False):
                continue  # passive monsters never move

            base_d = abs(px - x) + abs(py - y)
            pre_dir = _dir_from(px, py, x, y)

            best: tuple[str, int, int, int] | None = None
            for d in ORDER:
                if not self.is_open(year, x, y, d):
                    continue
                nx, ny = x + DIR[d][0], y + DIR[d][1]
                new_d = abs(px - nx) + abs(py - ny)
                if new_d < base_d:
                    cand = (d, nx, ny, new_d)
                    if (
                        best is None
                        or cand[3] < best[3]
                        or (
                            cand[3] == best[3] and ORDER.index(d) < ORDER.index(best[0])
                        )
                    ):
                        best = cand

            if best is None:
                continue  # no progress toward player

            d, nx, ny, ndist = best

            # Commit move
            lst = self._monsters.get((year, x, y)) or []
            try:
                lst.remove(m)
            except ValueError:
                pass
            if not lst:
                self._monsters.pop((year, x, y), None)
            else:
                self._monsters[(year, x, y)] = lst
            self._monsters.setdefault((year, nx, ny), []).append(m)

            if (nx, ny) == (px, py):
                mm2 = cast(MutableMapping[str, object], m)
                arrivals.append(
                    (int(cast(int, mm2["id"])), cast(str, mm2["name"]), pre_dir)
                )

            if footsteps_event is None:
                post_dx, post_dy = nx - px, ny - py
                if ndist == 2:
                    footsteps_event = ("loud", footstep_direction(post_dx, post_dy))
                elif 3 <= ndist <= 6:
                    footsteps_event = ("faint", footstep_direction(post_dx, post_dy))

        return arrivals, footsteps_event

    def shadow_dirs(self, year: int, x: int, y: int) -> list[Direction]:
        dirs: list[Direction] = []
        for d in ORDER:
            if self.is_open(year, x, y, d):
                nx, ny = x + DIR[d][0], y + DIR[d][1]
                if self.has_monster(year, nx, ny):
                    dirs.append(d)
        return dirs

    def adjacent_monster_names(
        self, year: int, x: int, y: int
    ) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        for d in ("east", "west", "north", "south"):
            if self.is_open(year, x, y, d):
                ax, ay = self.step(x, y, d)
                m = self.monster_here(year, ax, ay)
                if m:
                    mm = cast(Mapping[str, object], m)
                    key = cast(str, mm["key"])
                    name = monsters_mod.REGISTRY[key].name
                    results.append((name, key))
        return results

    def resolve_monster_prefix_nearby(
        self, year: int, x: int, y: int, query: str
    ) -> str | None:
        candidates: list[str] = []
        name_to_key: dict[str, str] = {}
        here = self.monster_here(year, x, y)
        if here:
            mh = cast(Mapping[str, object], here)
            key = cast(str, mh["key"])
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
            if (
                abs(x0 - x) + abs(y0 - y) <= radius
                or abs(x1 - x) + abs(y1 - y) <= radius
            ):
                hit = True
                break
        self._recent_monster_moves.clear()
        return hit

    def force_monster_move_within4(self, year: int = 2000) -> None:
        self._recent_monster_moves.append((year, 1, 0, 1, 1))

    def is_open(self, year: int, x: int, y: int, direction: Direction) -> bool:
        """Return ``True`` if moving from ``(x, y)`` in ``direction`` stays in bounds."""
        nx, ny = step(x, y, direction)
        return in_bounds(nx, ny)

    def step(self, x: int, y: int, direction: Direction) -> tuple[int, int]:
        """Return coordinates stepped one tile in ``direction`` from ``(x, y)``."""
        return step(x, y, direction)

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
        if value not in ALLOWED_CENTURIES:
            raise ValueError("Year must be one of the allowed centuries.")
        if value not in self.years:
            from . import gen

            grid = gen.generate(seed=value)
            # Ensure starting location is always open
            if not grid.is_walkable(0, 0):
                raise ValueError("start tile (0,0) must be open")
            self.years[value] = Year(value, grid)
            gen.seed_items(self, value, grid)
            had_start = self.has_monster(value, 0, 0)
            if self._seed_monsters:
                gen.seed_monsters_for_year(self, value, self.global_seed)
            # Ensure starting tile is clear unless a monster was explicitly placed
            if not had_start:
                while self.remove_monster(value, 0, 0):
                    pass
        return self.years[value]
