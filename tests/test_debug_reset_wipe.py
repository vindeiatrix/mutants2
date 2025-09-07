from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


def test_debug_reset(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    persistence.SAVE_PATH = tmp_path / "save.json"
    w = world_mod.World()
    p = Player()
    save = persistence.Save()
    persistence.save(p, w, save)
    assert persistence.SAVE_PATH.exists()
    persistence.debug_reset()
    assert not persistence.SAVE_PATH.exists()


def test_debug_wipe():
    w = world_mod.World()
    w.ground[(2000, 0, 0)] = [{"key": "test-item"}]
    p = Player()
    save = persistence.Save(profiles={"Warrior": {}})
    persistence.debug_wipe(p, w, save)
    assert w.ground == {}
    assert save.profiles == {}
