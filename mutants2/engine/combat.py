"""Simple combat helpers."""

from __future__ import annotations

from ..ui.theme import yellow
from .leveling import check_level_up

MONSTER_XP = 20_000


def award_kill(player) -> None:
    """Award XP for a monster kill and trigger level-up checks."""

    player.exp += MONSTER_XP
    print(yellow("***"))
    print(yellow("You gain 20,000 experience points!"))
    check_level_up(player)
