from .world import World
from .player import Player
from .senses import SensesCues
from . import items


def _dir_from_dxdy(dx: int, dy: int) -> str:
    if abs(dx) >= abs(dy):
        return "east" if dx > 0 else "west"
    return "south" if dy > 0 else "north"


def senses_lines(world: World, player: Player) -> list[str]:
    hit = world.nearest_monster(player.year, player.x, player.y, max_dist=4)
    lines: list[str] = []
    if hit:
        dx, dy, dist = hit
        if dist <= 2:
            lines.append(f"A shadow flickers to the {_dir_from_dxdy(dx, dy)}.")
        else:
            lines.append("You hear footsteps nearby.")
    return lines


def render_room_view(player: Player, world: World, *, consume_cues: bool = True) -> None:
    print("---")
    print(f"Class: {player.clazz}")
    print(f"{player.x}E : {player.y}N")
    lines = senses_lines(world, player)
    if consume_cues:
        cues = player.senses.pop()
    else:
        cues = SensesCues()
    for d in ("north", "south", "east", "west"):
        if d in cues.shadow_dirs:
            lines.append(f"A shadow flickers to the {d}.")
    if cues.footsteps_distance:
        mapping = {1: "very close", 2: "close", 3: "nearby", 4: "far away"}
        lines.append(f"You hear footsteps {mapping[cues.footsteps_distance]}.")
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
