from .world import World
from .player import Player
from .senses import SensesCues
from . import items


def render_room_view(player: Player, world: World, *, consume_cues: bool = True) -> None:
    print("---")
    print(f"Class: {player.clazz}")
    print(f"{player.x}E : {player.y}N")
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
    if consume_cues:
        cues = player.senses.pop()
    else:
        cues = SensesCues()
    for d in ("north", "south", "east", "west"):
        if d in cues.shadow_dirs:
            print(f"A shadow flickers to the {d}.")
    if cues.footsteps_distance:
        mapping = {1: "very close", 2: "close", 3: "nearby", 4: "far away"}
        print(f"You hear footsteps {mapping[cues.footsteps_distance]}.")


# Backwards compatibility
render = render_room_view
