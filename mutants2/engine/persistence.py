import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, Set

from .player import Player
from .world import World
from . import monsters as monsters_mod

from . import gen


@dataclass
class Save:
    """Metadata stored alongside the world/player state."""

    global_seed: int = gen.SEED
    last_topup_date: str | None = None
    # ``fake_today_override`` is session-only and not persisted
    fake_today_override: str | None = None


SAVE_PATH = Path(os.path.expanduser("~/.mutants2/save.json"))


def load() -> Tuple[Player, Dict[Tuple[int, int, int], list[str]], Dict[Tuple[int, int, int], dict], Set[int], Save]:
    try:
        with open(SAVE_PATH) as fh:
            data = json.load(fh)
        year = data.get("year", 2000)
        positions: Dict[int, Tuple[int, int]] = {
            int(k): (v.get("x", 0), v.get("y", 0))
            for k, v in data.get("positions", {}).items()
        }
        clazz = data.get("class")
        player = Player(year=year, clazz=clazz)
        player.positions.update(positions)
        player.max_hp = int(data.get("max_hp", player.max_hp))
        player.hp = int(data.get("hp", player.max_hp))
        player.inventory.update({k: int(v) for k, v in data.get("inventory", {}).items()})
        ground_raw = {
            tuple(int(n) for n in key.split(',')): val
            for key, val in data.get("ground", {}).items()
        }
        ground: Dict[Tuple[int, int, int], list[str]] = {}
        for coord, val in ground_raw.items():
            if isinstance(val, list):
                ground[coord] = list(val)
            else:
                ground[coord] = [val]
        monsters_data: Dict[Tuple[int, int, int], dict] = {}
        for key, val in data.get("monsters", {}).items():
            coord = tuple(int(n) for n in key.split(','))
            if isinstance(val, dict):
                m_key = val.get("key")
                hp = val.get("hp")
                name = val.get("name")
                # ``aggro`` state is persisted to keep passive monsters from moving
                aggro = val.get("aggro", False)
                seen = val.get("seen", False)
                mid = val.get("id")
            else:
                m_key = val
                hp = None
                name = None
                aggro = False
                seen = False
                mid = None
            if m_key is None:
                continue
            base = monsters_mod.REGISTRY[m_key].base_hp
            if mid is None:
                mid = monsters_mod.next_id()
            else:
                monsters_mod.note_existing_id(int(mid))
            m = {
                "key": m_key,
                "hp": int(hp) if hp is not None else base,
                "name": name or monsters_mod.REGISTRY[m_key].name,
                "aggro": bool(aggro),
                "seen": bool(seen),
                "id": int(mid),
            }
            if m.get("aggro") and not m.get("seen"):
                m["aggro"] = False
            monsters_data[coord] = m
        seeded = {int(y) for y in data.get("seeded_years", [])}
        save_meta = Save(
            global_seed=int(data.get("global_seed", gen.SEED)),
            last_topup_date=data.get("last_topup_date"),
        )
        return player, ground, monsters_data, seeded, save_meta
    except FileNotFoundError:
        player = Player()
        ground: Dict[Tuple[int, int, int], list[str]] = {}
        monsters_data: Dict[Tuple[int, int, int], dict] = {}
        seeded: Set[int] = set()
        save_meta = Save()
        save(player, World(ground, seeded, monsters_data, global_seed=save_meta.global_seed), save_meta)
        return player, ground, monsters_data, seeded, save_meta


def save(player: Player, world: World, save_meta: Save) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "w") as fh:
        data = {
            "year": player.year,
            "positions": {
                str(y): {"x": x, "y": yy}
                for y, (x, yy) in player.positions.items()
            },
            "class": player.clazz,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "inventory": {k: v for k, v in player.inventory.items()},
            "ground": {
                f"{y},{x},{yy}": (items[0] if len(items) == 1 else items)
                for (y, x, yy), items in world.ground.items()
            },
            "monsters": {
                f"{y},{x},{yy}": {
                    "key": data["key"],
                    "hp": data["hp"],
                    "name": data.get("name"),
                    "aggro": data.get("aggro", False),
                    "seen": data.get("seen", False),
                    "id": data.get("id"),
                }
                for (y, x, yy), data in world.monsters.items()
            },
            "seeded_years": list(world.seeded_years),
            "global_seed": save_meta.global_seed,
            "last_topup_date": save_meta.last_topup_date,
            # no senses data; cues are never persisted
        }
        json.dump(data, fh)
