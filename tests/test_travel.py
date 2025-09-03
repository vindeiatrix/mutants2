from mutants2.engine.world import World
from mutants2.engine.player import Player


def test_travel_and_positions():
    w = World()
    p = Player()
    assert p.move("east", w)
    assert (p.x, p.y, p.year) == (1, 0, 2000)

    p.travel(w)
    assert (p.year, p.x, p.y) == (2100, 0, 0)

    assert p.move("north", w)
    assert (p.x, p.y) == (0, 1)

    p.travel(w)
    assert (p.year, p.x, p.y) == (2000, 0, 0)

    assert p.move("east", w)
    assert (p.x, p.y) == (1, 0)
    p.travel(w, 2000)
    assert (p.year, p.x, p.y) == (2000, 0, 0)

    p.travel(w, 2100)
    assert (p.year, p.x, p.y) == (2100, 0, 0)

