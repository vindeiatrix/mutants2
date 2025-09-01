from mutants2.engine.world import World


def test_world_maps_have_origin_and_exits():
    w = World()
    for year in (2000, 2100, 2200):
        grid = w.year(year).grid
        assert grid.width == 30 and grid.height == 30
        assert grid.is_walkable(0, 0)
        assert grid.is_walkable(grid.width // 2, grid.height // 2)
        neighbors = grid.neighbors(0, 0)
        assert neighbors
        for nx, ny in neighbors.values():
            assert 0 <= nx < grid.width and 0 <= ny < grid.height
