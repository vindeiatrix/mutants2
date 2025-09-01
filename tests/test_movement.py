from mutants2.engine.world import World
from mutants2.engine.player import Player


def test_player_movement():
    w = World()
    p = Player()
    assert p.move('north', w)
    assert (p.x, p.y) == (0, 1)
    assert not p.move('west', w)
    assert (p.x, p.y) == (0, 1)
