from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Set, Tuple

from .player import Player
from .world import World
from . import monsters as monsters_mod
from .types import ItemListMut, MonsterRec, TileKey

from . import gen


@dataclass
class Save:
    """Metadata stored alongside the world/player state."""

    global_seed: int = gen.SEED
    last_topup_date: str | None = None
    # ``fake_today_override`` is session-only and not persisted
    fake_today_override: str | None = None


SAVE_PATH = Path(os.path.expanduser("~/.mutants2/save.json"))


def load() -> tuple[
    Player,
    dict[TileKey, ItemListMut],
    dict[TileKey, list[MonsterRec]],
    Set[int],
    Save,
]:
    try:
        with open(SAVE_PATH) as fh:
            data = json.load(fh)
        # Ignore legacy wall data if present
        data.pop("walls", None)
        data.pop("blocked", None)
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
        player.inventory.update(
            {k: int(v) for k, v in data.get("inventory", {}).items()}
        )
        player.ions = int(data.get("ions", 0))
        ground: dict[TileKey, ItemListMut] = {}
        for key, val in data.get("ground", {}).items():
            parts = [int(n) for n in key.split(",")]
            coord: TileKey = (parts[0], parts[1], parts[2])
            if isinstance(val, list):
                ground[coord] = list(val)
            else:
                ground[coord] = [val]
        monsters_data: dict[TileKey, list[MonsterRec]] = {}
        for key, val in data.get("monsters", {}).items():
            parts = [int(n) for n in key.split(",")]
            coord: TileKey = (parts[0], parts[1], parts[2])
            entries = val if isinstance(val, list) else [val]
            lst: list[MonsterRec] = []
            for entry in entries:
                m_key = entry.get("key")
                if m_key is None:
                    continue
                hp = entry.get("hp")
                name = entry.get("name")
                aggro = entry.get("aggro", False)
                seen = entry.get("seen", False)
                mid = entry.get("id")
                base = monsters_mod.REGISTRY[m_key].base_hp
                m: dict[str, object] = {
                    "key": m_key,
                    "hp": int(hp) if hp is not None else base,
                    "name": name or monsters_mod.REGISTRY[m_key].name,
                    "aggro": bool(aggro),
                    "seen": bool(seen),
                }
                if mid is not None:
                    m["id"] = int(mid)
                if m.get("aggro") and not m.get("seen"):
                    m["aggro"] = False
                lst.append(m)
            if lst:
                monsters_data[coord] = lst
        seeded = {int(y) for y in data.get("seeded_years", [])}
        save_meta = Save(
            global_seed=int(data.get("global_seed", gen.SEED)),
            last_topup_date=data.get("last_topup_date"),
        )
        return player, ground, monsters_data, seeded, save_meta
    except FileNotFoundError:
        player = Player()
        ground: dict[TileKey, ItemListMut] = {}
        monsters_data: dict[TileKey, list[MonsterRec]] = {}
        seeded: Set[int] = set()
        save_meta = Save()
        save(
            player,
            World(ground, seeded, monsters_data, global_seed=save_meta.global_seed),
            save_meta,
        )
        return player, ground, monsters_data, seeded, save_meta


def save(player: Player, world: World, save_meta: Save) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "w") as fh:
        data = {
            "year": player.year,
            "positions": {
                str(y): {"x": x, "y": yy} for y, (x, yy) in player.positions.items()
            },
            "class": player.clazz,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "inventory": {k: v for k, v in player.inventory.items()},
            "ions": player.ions,
            "ground": {
                f"{y},{x},{yy}": (items[0] if len(items) == 1 else items)
                for (y, x, yy), items in world.ground.items()
            },
            "monsters": {
                f"{y},{x},{yy}": (processed[0] if len(processed) == 1 else processed)
                for (y, x, yy), lst in world.monsters.items()
                for processed in [
                    [
                        {
                            "key": m["key"],
                            "hp": m["hp"],
                            "name": m.get("name"),
                            "aggro": m.get("aggro", False),
                            "seen": m.get("seen", False),
                            "id": m.get("id"),
                        }
                        for m in lst
                    ]
                ]
            },
            "seeded_years": list(world.seeded_years),
            "global_seed": save_meta.global_seed,
            "last_topup_date": save_meta.last_topup_date,
            # no senses data; cues are never persisted
        }
        json.dump(data, fh)
