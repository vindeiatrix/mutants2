from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.engine import persistence


def test_save_load(tmp_path, monkeypatch):
    monkeypatch.setenv('HOME', str(tmp_path))
    w = World()
    p = Player()
    assert p.move('east', w)
    p.travel(w)
    assert p.move('north', w)
    persistence.save(p)
    p2 = persistence.load()
    assert (p2.year, p2.x, p2.y) == (2100, 0, 1)
    p2.travel(w)
    assert (p2.x, p2.y) == (0, 0)
