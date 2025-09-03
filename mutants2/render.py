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


def render_room_at(world, year, x, y, *, include_shadows: bool = True, shadow_dirs_extra=()):
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

    # (d) separator
    out.append(SEP)

    # (e) ground items
    ground_names = [it.name for it in world.items_on_ground(year, x, y)]
    if ground_names:
        out.append(yellow("On the ground lies:"))
        line = ", ".join(stack_for_render(ground_names))
        out.append(cyan(line))
        out.append(SEP)

    # (g) monsters here
    here = list(world.monsters_here(year, x, y))
    if here:
        for m in here:
            name = m.get("name") or m.get("key")
            out.append(white(f"{name} is here."))
        out.append(SEP)

    # (i) shadows
    if include_shadows:
        dirs = set(shadow_dirs_extra)
        for d in ("east", "west", "north", "south"):
            if world.is_open(year, x, y, d):
                ax, ay = world.step(x, y, d)
                if world.has_monster(year, ax, ay):
                    dirs.add(d)
        if dirs:
            out.append(yellow(f"You see shadows to the {', '.join(sorted(dirs))}."))

    return "\n".join(out)


def render_current_room(player, world, *, include_shadows: bool = True):
    return render_room_at(world, player.year, player.x, player.y, include_shadows=include_shadows)
