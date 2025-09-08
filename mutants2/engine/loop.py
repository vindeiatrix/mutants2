from __future__ import annotations

import time
import threading

from ..data.config import ION_BASE
from ..ui.theme import yellow, SEP
from .player import class_key


def should_render_room(cmd: str, args: list[str], moved: bool) -> bool:
    """Return ``True`` if the full room view should be printed.

    Movement that actually changes the room and a bare ``look`` request
    trigger a render.  ``travel`` always suppresses the room block.
    """

    c = cmd.lower()
    if c in {"north", "south", "east", "west", "last"}:
        return moved
    if c == "look" and not args:
        return True
    return False


TICK_SECONDS = 10.0
REALTIME_TICK_POLL = 1.0
MAX_CATCHUP = 6


def game_is_active(context) -> bool:
    """Return ``True`` if ``context`` is actively in a running game."""

    return bool(
        context
        and getattr(context, "in_game", False)
        and getattr(context, "player", None)
        and getattr(context, "world", None)
        and not getattr(getattr(context, "player", None), "is_dead", lambda: False)()
    )


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

    if context is not None and not game_is_active(context):
        return False
    if hasattr(player, "is_dead") and player.is_dead():
        return False

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
            player.ready_to_combat_id = None
            player.ready_to_combat_name = None
            world.reset_aggro_in_year(player.year)
            if context is not None:
                context._arrivals_this_tick = []
                context._needs_render = False
                context._suppress_room_render = True
    return died


def maybe_process_upkeep(
    player, world, save, context=None, *, now: float | None = None
) -> None:
    """Process at most one upkeep/starvation tick on command edges."""

    if context is not None and getattr(context, "tick_handle", None):
        return

    current = time.monotonic() if now is None else now
    nxt = getattr(save, "next_upkeep_tick", None)
    if nxt is None:
        save.next_upkeep_tick = current + TICK_SECONDS
        return
    if current >= nxt and game_is_active(context):
        process_upkeep_and_starvation(player, world, save, context)
        save.next_upkeep_tick = current + TICK_SECONDS


def ion_upkeep(
    player,
    world,
    save,
    context=None,
    *,
    now: float | None = None,
    max_ticks: int | None = None,
) -> None:
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
        max_ticks = int(getattr(save, "max_catchup_ticks", MAX_CATCHUP))
    else:
        max_ticks = int(max_ticks)
    if ticks > max_ticks:
        ticks = max_ticks
    for _ in range(ticks):
        save.last_upkeep_tick += TICK_SECONDS
        if process_upkeep_and_starvation(player, world, save, context):
            break


def start_realtime_tick(player, world, save, context=None):
    """Start a background thread that applies upkeep in real time."""

    if context is not None and getattr(context, "tick_handle", None):
        return context.tick_handle

    stop_event = threading.Event()

    def _run() -> None:
        while not stop_event.is_set():
            time.sleep(REALTIME_TICK_POLL)
            if context is not None and not game_is_active(context):
                continue
            now = time.monotonic()
            nxt = getattr(save, "next_upkeep_tick", None)
            if nxt is None:
                save.next_upkeep_tick = now + TICK_SECONDS
                continue
            if now < nxt:
                continue
            process_upkeep_and_starvation(player, world, save, context)
            save.next_upkeep_tick = max(nxt + TICK_SECONDS, now + TICK_SECONDS)
            if context is not None and hasattr(context, "request_render"):
                context.request_render()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return stop_event, thread


def stop_realtime_tick(handle) -> None:
    """Stop a previously started realtime tick thread."""

    if handle is None:
        return
    stop_event, thread = handle
    stop_event.set()
    thread.join(timeout=1)
