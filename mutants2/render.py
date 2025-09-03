from __future__ import annotations

from .ui.theme import red, green, cyan, yellow, white, SEP
from .engine.items import stack_for_render


def _room_desc(world, year, x, y):
    if hasattr(world, "room_description"):
        try:
            return world.room_description(year, x, y)
        except Exception:
            pass
    return "You are here."


def render_room_at(
    world,
    year,
    x,
    y,
    *,
    include_shadows: bool = True,
    shadow_dirs_extra=(),
    context=None,
):
    """Render the room at ``(year, x, y)``.

    When ``context`` is provided, it may carry pre-computed shadow and arrival
    information produced during the current tick.  This function is responsible
    for ordering those events and suppressing presence lines when arrivals
    occurred.
    """

    out: list[str] = []

    # (a) room description
    out.append(red(_room_desc(world, year, x, y)))

    # (b) compass line
    cx = f"{x}E"
    cy = f"{y}N"
    out.append(green(f"Compass: ({cx} : {cy})"))

    # (c) exits
    for d in ("north", "south", "east", "west"):
        if world.is_open(year, x, y, d):
            out.append(cyan(f"{d} – area continues."))

    # (d/e) ground items followed by a single separator
    ground_names = [it.name for it in world.items_on_ground(year, x, y)]
    if ground_names:
        out.append(yellow("On the ground lies:"))
        line = ", ".join(stack_for_render(ground_names))
        out.append(cyan(line))
    # Always end the header section with one separator
    out.append(SEP)

    shadow_lines: list[str] = []
    if include_shadows:
        if context is not None:
            pre = getattr(context, "_pre_shadow_lines", []) or []
            if pre:
                shadow_lines = [yellow(s) for s in pre]
            context._pre_shadow_lines = []
        if not shadow_lines:
            dirs = set(shadow_dirs_extra)
            for d in ("east", "west", "north", "south"):
                if world.is_open(year, x, y, d):
                    ax, ay = world.step(x, y, d)
                    if world.has_monster(year, ax, ay):
                        dirs.add(d)
            if dirs:
                shadow_lines = [
                    yellow(f"You see shadows to the {', '.join(sorted(dirs))}.")
                ]

    arrivals = []
    if context is not None:
        arrivals = getattr(context, "_arrivals_this_tick", []) or []

    if shadow_lines:
        out.extend(shadow_lines)
    if shadow_lines and arrivals:
        out.append(SEP)
    if arrivals:
        for msg in arrivals:
            out.append(red(msg))
        if context is not None:
            context._suppress_presence_this_tick = True
    else:
        if context is not None:
            context._suppress_presence_this_tick = False

    if context is not None:
        context._arrivals_this_tick = []

    # Presence lines only when no arrivals were printed
    if not arrivals:
        here = list(world.monsters_here(year, x, y))
        if here:
            for m in here:
                name = m.get("name") or m.get("key")
                out.append(white(f"{name} is here."))

    return "\n".join(out)


def render_current_room(player, world, *, include_shadows: bool = True, context=None):
    return render_room_at(
        world,
        player.year,
        player.x,
        player.y,
        include_shadows=include_shadows,
        context=context,
    )
