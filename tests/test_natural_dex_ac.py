import pytest
from mutants2.engine.player import Player
from mutants2.engine import items
from mutants2.data.class_tables import BASE_LEVEL1
from mutants2.engine.items import ItemDef


def test_natural_dex_ac_values():
    cases = {9: 1, 10: 2, 19: 2, 20: 3, 29: 3, 30: 4}
    for dex, expected in cases.items():
        p = Player()
        p.dexterity = dex
        p.recompute_ac()
        assert p.natural_dex_ac == expected
        assert p.ac_total == expected


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


@pytest.mark.parametrize("clazz", list(BASE_LEVEL1.keys()))
def test_classes_starting_ac(clazz):
    p = Player(clazz=clazz)
    assert p.ac_total == 1 + (p.dexterity // 10)


def test_ac_totals_with_bonus_seven():
    temp = ItemDef("temp_arm", "Temp-Arm", 0, None, None, False, None, 0, 7, 0, None)
    items.REGISTRY["temp_arm"] = temp
    for dex, total in zip([0, 10, 20, 30, 40], [8, 9, 10, 11, 12]):
        p = Player()
        p.dexterity = dex
        p.worn_armor = {"key": "temp_arm"}
        p.recompute_ac()
        assert p.ac_total == total
    del items.REGISTRY["temp_arm"]
