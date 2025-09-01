from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.engine import persistence


def test_save_load(tmp_path, monkeypatch):
    monkeypatch.setenv('HOME', str(tmp_path))
    w = World()
    p = Player()
    assert p.move('east', w)
    persistence.save(p)
    p2 = persistence.load()
    assert (p2.x, p2.y) == (1, 0)
