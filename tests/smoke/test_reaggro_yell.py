from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.engine.ai import set_aggro


def test_reaggro_yell_after_reload(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"

    w = world_mod.World()
    w.year(2000)
    for (x, y), _ in list(w.monsters_in_year(2000).items()):
        w.remove_monster(2000, x, y)
    w.place_monster(2000, 0, 0, "mutant")
    m = w.monster_here(2000, 0, 0)

    p = Player(year=2000, clazz="Warrior")
    save = persistence.Save()

    first = set_aggro(m)
    assert first and "yells at you" in first
    assert set_aggro(m) is None

    w.reset_all_aggro()
    persistence.save(p, w, save)
    p2, ground, monsters, seeded, save2 = persistence.load()
    w2 = world_mod.World(ground, seeded, monsters, global_seed=save2.global_seed)
    m2 = w2.monster_here(p2.year, p2.x, p2.y)

    again = set_aggro(m2)
    assert again and "yells at you" in again
    assert set_aggro(m2) is None
