from __future__ import annotations

import time
import threading

from ..data.config import ION_BASE
from ..ui.theme import yellow, SEP
from .player import class_key

TICK_SECONDS = 10.0
REALTIME_TICK_POLL = 1.0


def ion_upkeep_per_tick(player) -> int:
    """Return ions to consume for a single upkeep tick."""

    if player.level <= 1:
        return 0
    clazz = class_key(player.clazz or "")
    base = ION_BASE.get(clazz, 0)
    steps = 1 + ((player.level - 2) // 2)
    return base * steps


def process_upkeep_and_starvation(player, world, save, context=None) -> bool:
    """Consume upkeep and apply starvation/death effects for one tick.

    Returns ``True`` if the player died during this tick.
    """

    consume = ion_upkeep_per_tick(player)
    if player.ions >= consume:
        player.ions -= consume
    else:
        player.ions = 0
    died = False
    if player.ions == 0 and not player.is_dead():
        player.hp = max(0, player.hp - player.level)
        print(SEP)
        print(yellow("You're starving for IONS!"))
        if player.hp <= 0:
            died = True
            print("You have died.")
            player.heal_full()
            player.positions[player.year] = (0, 0)
            world.reset_aggro_in_year(player.year)
            if context is not None:
                context._arrivals_this_tick = []
                context._needs_render = False
                context._suppress_room_render = True
    return died


def maybe_process_upkeep(player, world, save, context=None, *, now: float | None = None) -> None:
    """Process at most one owed upkeep/starvation tick based on ``last_upkeep_tick``."""

    current = time.monotonic() if now is None else now
    last = getattr(save, "last_upkeep_tick", None)
    if last is None:
        save.last_upkeep_tick = current
        return
    ticks = int((current - last) // TICK_SECONDS)
    if ticks >= 1:
        save.last_upkeep_tick += TICK_SECONDS
        process_upkeep_and_starvation(player, world, save, context)


def ion_upkeep(player, world, save, context=None, *, now: float | None = None, max_ticks: int | None = None) -> None:
    """Catch up on ion upkeep immediately (used for tests/offline processing)."""

    current = time.monotonic() if now is None else now
    last = getattr(save, "last_upkeep_tick", None)
    if last is None:
        save.last_upkeep_tick = current
        return
    elapsed = current - last
    ticks = int(elapsed // TICK_SECONDS)
    if ticks <= 0:
        return
    if max_ticks is None:
        max_ticks = getattr(save, "max_catchup_ticks", 60)
    if ticks > max_ticks:
        ticks = max_ticks
    for _ in range(ticks):
        save.last_upkeep_tick += TICK_SECONDS
        if process_upkeep_and_starvation(player, world, save, context):
            break


def start_realtime_tick(player, world, save, context=None):
    """Start a background thread that applies upkeep in real time."""

    stop_event = threading.Event()

    def _run() -> None:
        while not stop_event.is_set():
            time.sleep(REALTIME_TICK_POLL)
            current = time.monotonic()
            ticks = int((current - save.last_upkeep_tick) // TICK_SECONDS)
            if ticks >= 1:
                save.last_upkeep_tick += TICK_SECONDS
                process_upkeep_and_starvation(player, world, save, context)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return stop_event, thread


def stop_realtime_tick(handle) -> None:
    """Stop a previously started realtime tick thread."""

    stop_event, thread = handle
    stop_event.set()
    thread.join(timeout=1)
