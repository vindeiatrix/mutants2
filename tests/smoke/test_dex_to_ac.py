from mutants2.engine.player import Player


def test_dex_to_ac():
    p = Player()
    p.dexterity = 25
    p.recompute_ac()
    assert p.natural_dex_ac == 2
    assert p.ac_total == 2
