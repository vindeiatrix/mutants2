from .world import World
from .player import Player
from .senses import SensesCues
from . import items, monsters


def shadow_lines(world: World, player: Player) -> list[str]:
    ds = world.shadow_dirs(player.year, player.x, player.y)
    return [f"You see shadows to the {', '.join(ds)}."] if ds else []


def entry_yell_lines(ctx) -> list[str]:
    lines = getattr(ctx, "_entry_yells", []) or []
    ctx._entry_yells = []
    return lines


def arrival_lines(ctx) -> list[str]:
    msgs = getattr(ctx, "_arrivals_this_tick", []) or []
    ctx._arrivals_this_tick = []
    return msgs


def footsteps_lines(ctx) -> list[str]:
    ev = getattr(ctx, "_footsteps_event", None)
    ctx._footsteps_event = None
    if not ev:
        return []
    kind, d = ev
    if kind == "faint":
        return [f"You hear faint sounds of footsteps far to the {d}."]
    else:
        return [f"You hear loud sounds of footsteps to the {d}."]


def render_room_view(player: Player, world: World, context=None, *, consume_cues: bool = True) -> None:
    print("---")
    print(f"Class: {player.clazz}")
    print(f"{player.x}E : {player.y}N")
    lines: list[str] = []
    if context is not None and getattr(context, "_pre_shadow_lines", None):
        lines.extend(context._pre_shadow_lines)
        context._pre_shadow_lines = []
    else:
        lines.extend(shadow_lines(world, player))
    if context is not None:
        lines.extend(getattr(context, "_entry_yells", []) or [])
        context._entry_yells = []
        lines.extend(arrival_lines(context))
        ev = getattr(context, "_footsteps_event", None)
        context._footsteps_event = None
        if ev:
            kind, d = ev
            if kind == "faint":
                lines.append(f"You hear faint sounds of footsteps far to the {d}.")
            else:
                lines.append(f"You hear loud sounds of footsteps to the {d}.")
    if consume_cues:
        cues = player.senses.pop()
    else:
        cues = SensesCues()
    for d in ("north", "south", "east", "west"):
        if d in cues.shadow_dirs:
            lines.append(f"A shadow flickers to the {d}.")
    m = world.monster_here(player.year, player.x, player.y)
    if m:
        name = m.get("name") or monsters.REGISTRY[m["key"]].name
        lines.append(f"{name} is here.")
    for line in lines:
        print(line)
    grid = world.year(player.year).grid
    neighbors = grid.neighbors(player.x, player.y)
    for direction in sorted(neighbors):
        print(f"{direction} - open passage.")
    print("***")
    item_key = world.ground_item(player.year, player.x, player.y)
    if item_key:
        name = items.REGISTRY[item_key].name
        print(f"On the ground lies: {name}")
    else:
        print("On the ground lies: (nothing)")
    if context is not None:
        pass


# Backwards compatibility
render = render_room_view
