from mutants2.engine.player import Player


def test_natural_dex_ac_values():
    cases = {9: 0, 10: 1, 15: 1, 29: 2, 30: 3}
    for dex, expected in cases.items():
        p = Player()
        p.dexterity = dex
        p.recompute_ac()
        assert p.natural_dex_ac == expected
        assert p.ac_total == p.ac + expected


def test_ac_total_with_armor():
    p = Player()
    p.dexterity = 15
    p.recompute_ac()
    base = p.ac_total
    p.worn_armor = {"key": "bug-skin"}
    p.recompute_ac()
    assert p.ac_total == base + 3
    p.worn_armor = None
    p.recompute_ac()
    assert p.ac_total == base
