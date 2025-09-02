import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, Set

from .player import Player
from .world import World

from . import gen


@dataclass
class Save:
    """Metadata stored alongside the world/player state."""

    global_seed: int = gen.SEED
    last_topup_date: str | None = None
    # ``fake_today_override`` is session-only and not persisted
    fake_today_override: str | None = None


SAVE_PATH = Path(os.path.expanduser("~/.mutants2/save.json"))


def load() -> Tuple[Player, Dict[Tuple[int, int, int], str], Set[int], Save]:
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
        player.inventory.update({k: int(v) for k, v in data.get("inventory", {}).items()})
        ground = {
            tuple(int(n) for n in key.split(',')): val
            for key, val in data.get("ground", {}).items()
        }
        seeded = {int(y) for y in data.get("seeded_years", [])}
        save_meta = Save(
            global_seed=int(data.get("global_seed", gen.SEED)),
            last_topup_date=data.get("last_topup_date"),
        )
        return player, ground, seeded, save_meta
    except FileNotFoundError:
        player = Player()
        ground: Dict[Tuple[int, int, int], str] = {}
        seeded: Set[int] = set()
        save_meta = Save()
        save(player, World(ground, seeded), save_meta)
        return player, ground, seeded, save_meta


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
            "inventory": {k: v for k, v in player.inventory.items()},
            "ground": {
                f"{y},{x},{yy}": item_key
                for (y, x, yy), item_key in world.ground.items()
            },
            "seeded_years": list(world.seeded_years),
            "global_seed": save_meta.global_seed,
            "last_topup_date": save_meta.last_topup_date,
            # no senses data; cues are never persisted
        }
        json.dump(data, fh)
