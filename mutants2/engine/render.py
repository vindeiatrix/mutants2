from .world import World
from .player import Player
from .senses import SensesCues
from . import items, monsters


def shadow_lines(world: World, player: Player) -> list[str]:
    ds = world.shadow_dirs(player.year, player.x, player.y)
    return [f"You see shadows to the {', '.join(ds)}."] if ds else []


def arrival_lines(ctx) -> list[str]:
    msgs = getattr(ctx, "_arrivals_this_tick", []) or []
    ctx._arrivals_this_tick = []
    return msgs


def audio_lines(ctx) -> list[str]:
    out: list[str] = []
    f = getattr(ctx, "_footstep_dir", None)
    y = getattr(ctx, "_yell_dir", None)
    if f:
        parts = f.split()
        kind = parts[0]
        d = parts[-1]
        if kind == "faint":
            out.append(f"You hear faint sounds of footsteps far to the {d}.")
        else:
            out.append(f"You hear loud sounds of footsteps to the {d}.")
    if y:
        parts = y.split()
        kind = parts[0]
        d = parts[-1]
        if kind == "faint":
            out.append(f"You hear faint sounds of yelling and screaming far to the {d}.")
        else:
            out.append(f"You hear loud sounds of yelling and screaming to the {d}.")
    ctx._footstep_dir = None
    ctx._yell_dir = None
    return out


def render_room_view(player: Player, world: World, context=None, *, consume_cues: bool = True) -> None:
    print("---")
    print(f"Class: {player.clazz}")
    print(f"{player.x}E : {player.y}N")
    lines: list[str] = []
    lines.extend(shadow_lines(world, player))
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
