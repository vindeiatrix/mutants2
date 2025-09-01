from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class Player:
    """Player state including position for each year."""

    year: int = 2000
    positions: Dict[int, Tuple[int, int]] = field(
        default_factory=lambda: {2000: (0, 0), 2100: (0, 0)}
    )

    @property
    def x(self) -> int:
        return self.positions[self.year][0]

    @property
    def y(self) -> int:
        return self.positions[self.year][1]

    def move(self, direction: str, world) -> bool:
        x, y = self.positions.setdefault(self.year, (0, 0))
        grid = world.year(self.year).grid
        neighbors = grid.neighbors(x, y)
        if direction in neighbors:
            self.positions[self.year] = neighbors[direction]
            return True
        return False

    def travel(self, world) -> None:
        """Switch between the two available years."""
        self.year = 2100 if self.year == 2000 else 2000
        world.year(self.year)  # ensure world generation
        self.positions.setdefault(self.year, (0, 0))

