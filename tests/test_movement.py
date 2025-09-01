from mutants2.engine.world import World
from mutants2.engine.player import Player


def test_player_movement(capsys):
    w = World()
    p = Player()
    assert p.move('north', w)
    assert (p.x, p.y) == (0, 1)
    assert not p.move('west', w)
    out = capsys.readouterr().out
    assert "can't go that way." in out
    assert (p.x, p.y) == (0, 1)


def test_diagonal_rejected(capsys):
    w = World()
    p = Player()
    assert not p.move('northwest', w)
    out = capsys.readouterr().out
    assert "can't go that way." in out
    assert (p.x, p.y) == (0, 0)
