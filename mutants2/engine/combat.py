"""Simple combat helpers."""

from __future__ import annotations

from .leveling import check_level_up

MONSTER_XP = 20_000


def award_kill(player) -> int:
    """Award XP for a monster kill and trigger level-up checks.

    Returns the amount of experience awarded.
    """

    player.exp += MONSTER_XP
    check_level_up(player)
    return MONSTER_XP
