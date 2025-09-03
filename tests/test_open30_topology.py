from mutants2.engine.world import World, GRID_MIN, GRID_MAX


def test_interior_has_four_exits():
    world = World()
    x, y = 0, 0
    dirs = ["north", "south", "east", "west"]
    assert all(world.is_open(world.year, x, y, d) for d in dirs)


def test_edges_block_out_of_bounds():
    world = World()
    x, y = GRID_MAX - 1, 0
    assert not world.is_open(world.year, x, y, "east")
    assert world.is_open(world.year, x, y, "west")


def test_corners_have_two_exits():
    world = World()
    x, y = GRID_MIN, GRID_MIN
    allowed = sum(
        world.is_open(world.year, x, y, d) for d in ["north", "south", "east", "west"]
    )
    assert allowed == 2


def test_walkable_coords_count():
    world = World()
    assert len(list(world.walkable_coords(world.year))) == 30 * 30
