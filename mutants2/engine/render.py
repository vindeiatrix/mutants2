from .world import World
from .player import Player
from .senses import SensesCues
from . import items


def _adjacent_dirs() -> tuple[str, ...]:
    return ("east", "west", "north", "south")


def senses_lines_for_tile(world: World, year: int, x: int, y: int) -> list[str]:
    lines: list[str] = []
    for d in _adjacent_dirs():
        if world.is_open(year, x, y, d):
            ax, ay = world.step(x, y, d)
            if world.has_monster(year, ax, ay):
                lines.append(f"A shadow flickers to the {d}.")
                break
    return lines


def render_room_view(player: Player, world: World, *, consume_cues: bool = True) -> None:
    print("---")
    print(f"Class: {player.clazz}")
    print(f"{player.x}E : {player.y}N")
    lines = senses_lines_for_tile(world, player.year, player.x, player.y)
    if consume_cues:
        cues = player.senses.pop()
    else:
        cues = SensesCues()
    for d in ("north", "south", "east", "west"):
        if d in cues.shadow_dirs:
            lines.append(f"A shadow flickers to the {d}.")
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


# Backwards compatibility
render = render_room_view
