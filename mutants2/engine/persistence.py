import json
import os
from pathlib import Path
from typing import Dict, Tuple

from .player import Player

SAVE_PATH = Path(os.path.expanduser('~/.mutants2/save.json'))


def load() -> Player:
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
        # Senses are ephemeral and intentionally not loaded
        return player
    except FileNotFoundError:
        player = Player()
        save(player)
        return player


def save(player: Player) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "w") as fh:
        data = {
            "year": player.year,
            "positions": {
                str(y): {"x": x, "y": yy}
                for y, (x, yy) in player.positions.items()
            },
            "class": player.clazz,
            # no senses data; cues are never persisted
        }
        json.dump(data, fh)
