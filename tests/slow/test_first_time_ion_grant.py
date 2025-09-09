from mutants2.engine import persistence
from mutants2.engine.player import Player
from mutants2.engine.state import ensure_first_time_ion_grant
from mutants2.engine.world import World


def test_first_time_ions_granted_once(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"
    w = World()
    p = Player(clazz="Warrior")
    save = persistence.Save()

    granted = ensure_first_time_ion_grant(p, save)
    assert granted
    persistence.save(p, w, save)
    assert p.ions == 30000

    p2, ground, monsters, seeded, save2 = persistence.load()
    _ = World(ground, seeded, monsters)
    granted2 = ensure_first_time_ion_grant(p2, save2)
    assert not granted2
    assert p2.ions == 30000
