from mutants2.engine.world import World


def test_monster_ids_unique_and_reusable():
    w = World()
    w.year(2000)
    # clear any default monsters
    for x, y, _ in list(w.monster_positions(2000)):
        w.remove_monster(2000, x, y)

    w.place_monster(2000, 0, 0, "mutant")
    w.place_monster(2000, 1, 0, "gargoyle")

    m1 = w.monster_here(2000, 0, 0)
    m2 = w.monster_here(2000, 1, 0)

    n1 = m1["id"]
    n2 = m2["id"]
    assert n1 != n2 and 1000 <= n1 <= 9999 and 1000 <= n2 <= 9999
    assert m1["name"] == f"Mutant-{n1:04d}"
    assert m2["name"] == f"Gargoyle-{n2:04d}"

    # kill first monster, its number should be reusable
    w.damage_monster(2000, 0, 0, 99)
    w.place_monster(2000, 2, 0, "kraken")
    m3 = w.monster_here(2000, 2, 0)
    assert m3["id"] == n1
    assert m3["name"] == f"Kraken-{n1:04d}"
