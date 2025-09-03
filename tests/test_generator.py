from mutants2.engine import gen
from mutants2.engine.world import GRID_MIN, GRID_MAX


def test_generator_basics():
    grid = gen.generate()
    assert grid.width == GRID_MAX - GRID_MIN and grid.height == GRID_MAX - GRID_MIN
    assert grid.is_walkable(0, 0)
    exits = grid.neighbors(0, 0)
    assert exits
    for nx, ny in exits.values():
        assert GRID_MIN <= nx < GRID_MAX and GRID_MIN <= ny < GRID_MAX
