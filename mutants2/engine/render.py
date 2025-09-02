from .world import World
from .player import Player
from .senses import SensesCues
from . import items, monsters


def shadow_line(world: World, year: int, x: int, y: int) -> list[str]:
    for d in ("east", "west", "north", "south"):
        if world.is_open(year, x, y, d):
            ax, ay = world.step(x, y, d)
            if world.has_monster(year, ax, ay):
                return [f"A shadow flickers to the {d}."]
    return []


def footsteps_line(ctx) -> list[str]:
    return ["You hear footsteps nearby."] if getattr(ctx, "_footsteps_this_tick", False) else []


def render_room_view(player: Player, world: World, context=None, *, consume_cues: bool = True) -> None:
    print("---")
    print(f"Class: {player.clazz}")
    print(f"{player.x}E : {player.y}N")
    lines: list[str] = []
    lines.extend(shadow_line(world, player.year, player.x, player.y))
    lines.extend(footsteps_line(context))
    if consume_cues:
        cues = player.senses.pop()
    else:
        cues = SensesCues()
    for d in ("north", "south", "east", "west"):
        if d in cues.shadow_dirs:
            lines.append(f"A shadow flickers to the {d}.")
    m = world.monster_here(player.year, player.x, player.y)
    if m:
        name = monsters.REGISTRY[m["key"]].name
        lines.append(f"A {name} is here.")
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
        context._footsteps_this_tick = False


# Backwards compatibility
render = render_room_view
