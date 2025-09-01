from dataclasses import dataclass


@dataclass
class Player:
    x: int = 0
    y: int = 0
    year: int = 2000

    def move(self, direction: str, world) -> bool:
        grid = world.year(self.year).grid
        neighbors = grid.neighbors(self.x, self.y)
        if direction in neighbors:
            self.x, self.y = neighbors[direction]
            return True
        return False
