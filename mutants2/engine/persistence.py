import json
import os
from pathlib import Path

from .player import Player

SAVE_PATH = Path(os.path.expanduser('~/.mutants2/save.json'))


def load() -> Player:
    try:
        with open(SAVE_PATH) as fh:
            data = json.load(fh)
        return Player(x=data.get('x', 0), y=data.get('y', 0), year=data.get('year', 2000))
    except FileNotFoundError:
        player = Player()
        save(player)
        return player


def save(player: Player) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, 'w') as fh:
        json.dump({'x': player.x, 'y': player.y, 'year': player.year}, fh)
