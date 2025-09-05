from __future__ import annotations

import time

from ..data.config import ION_BASE
from ..ui.theme import yellow
from .player import class_key


def ion_upkeep(player, world, save, context=None, *, now: float | None = None, max_ticks: int = 60) -> None:
    """Apply ion upkeep based on elapsed time.

    This subtracts ions every 10 seconds according to class and level.
    If ions run out, the player loses HP equal to their level each tick.
    """

    current = time.time() if now is None else now
    last = getattr(save, "last_ion_tick", None)
    if last is None:
        save.last_ion_tick = current
        return
    elapsed = current - last
    ticks = int(elapsed // 10)
    if ticks <= 0:
        return
    if ticks > max_ticks:
        ticks = max_ticks
    save.last_ion_tick = last + ticks * 10
    clazz = class_key(player.clazz or "")
    base = ION_BASE.get(clazz, 0)
    for _ in range(ticks):
        if player.level > 1:
            mult = 2 ** ((player.level - 2) // 2)
            consume = base * mult
        else:
            consume = 0
        if player.ions >= consume:
            player.ions -= consume
        else:
            player.ions = 0
        if player.ions == 0:
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
