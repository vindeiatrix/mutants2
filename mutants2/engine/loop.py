from __future__ import annotations

import time

from ..data.config import ION_BASE
from ..ui.theme import yellow
from .player import class_key


def ion_upkeep_per_tick(player) -> int:
    """Return ions to consume for a single 10 second tick."""

    if player.level <= 1:
        return 0
    clazz = class_key(player.clazz or "")
    base = ION_BASE.get(clazz, 0)
    steps = 1 + ((player.level - 2) // 2)
    return base * steps


def ion_upkeep(player, world, save, context=None, *, now: float | None = None, max_ticks: int = 60) -> None:
    """Apply ion upkeep and starvation based on elapsed time."""

    current = time.time() if now is None else now
    last = getattr(save, "last_upkeep_tick", None)
    if last is None:
        save.last_upkeep_tick = current
        return
    elapsed = current - last
    ticks = int(elapsed // 10)
    if ticks <= 0:
        return
    if ticks > max_ticks:
        ticks = max_ticks
    for _ in range(ticks):
        last += 10
        consume = ion_upkeep_per_tick(player)
        if player.ions >= consume:
            player.ions -= consume
        else:
            player.ions = 0
        if player.ions == 0 and not player.is_dead():
            player.hp = max(0, player.hp - player.level)
            print(yellow("You're starving for IONS!"))
            if player.hp <= 0:
                print("You have died.")
                player.heal_full()
                player.positions[player.year] = (0, 0)
                world.reset_aggro_in_year(player.year)
                if context is not None:
                    context._arrivals_this_tick = []
                    context._needs_render = False
                    context._suppress_room_render = True
                break
    save.last_upkeep_tick = last
