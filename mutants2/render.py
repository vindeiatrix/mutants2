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
    include_arrivals: bool = True,
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
            # Pad direction labels to align the separator across lines.
            out.append(cyan(f"{d:<5} – area continues."))

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

    arrivals_all: list[tuple[int, str, str]] = []
    arrivals_for_render: list[tuple[int, str, str]] = []
    if context is not None:
        arrivals_all = getattr(context, "_arrivals_this_tick", []) or []
        if include_arrivals:
            context._arrivals_this_tick = []
            arrivals_for_render = arrivals_all

    arrival_ids = {aid for aid, *_ in arrivals_all}
    monsters_here = world.monsters_here(year, x, y)
    residents = (
        [m for m in monsters_here if m.get("id") not in arrival_ids]
        if arrivals_all
        else monsters_here
    )

    names = [m.get("name") or m.get("key") for m in residents]
    if names:
        if len(names) == 1:
            line = f"{names[0]} is here."
        elif len(names) == 2:
            line = f"{names[0]}, and {names[1]} are here with you."
        else:
            line = f"{', '.join(names[:-1])}, and {names[-1]} are here with you."
        out.append(white(line))
        if shadow_lines or arrivals_for_render:
            out.append(SEP)

    if shadow_lines:
        out.extend(shadow_lines)
        if arrivals_for_render:
            out.append(SEP)

    if arrivals_for_render:
        arr_sorted = sorted(arrivals_for_render)
        for i, (aid, name, d) in enumerate(arr_sorted):
            out.append(red(f"{name} has just arrived from the {d}."))
            if i < len(arr_sorted) - 1:
                out.append(SEP)

    return "\n".join(out)


def render_current_room(
    player,
    world,
    *,
    include_shadows: bool = True,
    context=None,
    include_arrivals: bool = True,
):
    return render_room_at(
        world,
        player.year,
        player.x,
        player.y,
        include_shadows=include_shadows,
        context=context,
        include_arrivals=include_arrivals,
    )
