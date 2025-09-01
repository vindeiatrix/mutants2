from mutants2.engine import gen


def test_generator_basics():
    grid = gen.generate()
    assert grid.width == 30 and grid.height == 30
    # center walkable
    assert grid.is_walkable(15, 15)
    # (0,0) has exits within bounds
    exits = grid.neighbors(0, 0)
    assert exits
    for nx, ny in exits.values():
        assert 0 <= nx < 30 and 0 <= ny < 30
