from mutants2.engine.world import World, GRID_MIN, GRID_MAX, ALLOWED_CENTURIES


def test_world_maps_have_origin_and_exits():
    w = World()
    for year in ALLOWED_CENTURIES:
        grid = w.year(year).grid
        assert grid.width == GRID_MAX - GRID_MIN and grid.height == GRID_MAX - GRID_MIN
        assert grid.is_walkable(0, 0)
        assert grid.is_walkable(1, 1)
        neighbors = grid.neighbors(0, 0)
        assert neighbors
        for nx, ny in neighbors.values():
            assert GRID_MIN <= nx < GRID_MAX and GRID_MIN <= ny < GRID_MAX
