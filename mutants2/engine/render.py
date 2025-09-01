from .world import World
from .player import Player


def render(player: Player, world: World) -> None:
    print("---")
    print(f"{player.x}E : {player.y}N")
    grid = world.year(player.year).grid
    neighbors = grid.neighbors(player.x, player.y)
    for direction in sorted(neighbors):
        print(f"{direction} - open passage.")
    print("***")
    print("On the ground lies: ")
