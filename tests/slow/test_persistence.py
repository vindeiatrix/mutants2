from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.engine import persistence


def test_save_load(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    persistence.SAVE_PATH = tmp_path / ".mutants2" / "save.json"
    w = World()
    p = Player()
    assert p.move("east", w)
    p.travel(w, 2100)
    assert p.move("north", w)
    save = persistence.Save()
    persistence.save(p, w, save)
    p2, ground, monsters, seeded, _ = persistence.load()
    assert (p2.year, p2.x, p2.y) == (2100, 0, 1)
    w2 = World(ground, seeded, monsters)
    p2.travel(w2, 2000)
    assert (p2.x, p2.y) == (0, 0)
