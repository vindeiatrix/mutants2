import pytest
from mutants2.engine.player import Player
from mutants2.engine import leveling
from mutants2.data.class_tables import BASE_LEVEL1, PROGRESSION

ATTR_MAP = {
    "str": "strength",
    "int": "intelligence",
    "wis": "wisdom",
    "dex": "dexterity",
    "con": "constitution",
    "cha": "charisma",
}


@pytest.mark.parametrize("clazz", list(BASE_LEVEL1.keys()))
def test_level1_stats(clazz):
    p = Player(clazz=clazz)
    base = BASE_LEVEL1[clazz]
    assert p.max_hp == base["hp"]
    assert p.hp == base["hp"]
    for short, attr in ATTR_MAP.items():
        assert getattr(p, attr) == base[short]


@pytest.mark.parametrize("clazz", list(BASE_LEVEL1.keys()))
def test_progression_to_level5(clazz):
    p = Player(clazz=clazz)
    table = PROGRESSION[clazz]
    target = 5
    p.exp = table[target]["xp_to_reach"]
    leveling.check_level_up(p)
    assert p.level == target
    base = BASE_LEVEL1[clazz]
    hp_expected = base["hp"] + sum(
        table[lvl]["hp_plus"] for lvl in range(2, target + 1)
    )
    assert p.max_hp == hp_expected
    for short, attr in ATTR_MAP.items():
        expected = base[short] + sum(
            table[lvl][f"{short}_plus"] for lvl in range(2, target + 1)
        )
        assert getattr(p, attr) == expected


def test_levels_beyond_eleven():
    clazz = "mage"
    p = Player(clazz=clazz)
    table = PROGRESSION[clazz]
    xp11 = table[11]["xp_to_reach"]
    p.exp = (13 - 10) * xp11
    leveling.check_level_up(p)
    assert p.level == 13
    base = BASE_LEVEL1[clazz]
    hp_expected = (
        base["hp"]
        + sum(table[lvl]["hp_plus"] for lvl in range(2, 12))
        + table[11]["hp_plus"] * 2
    )
    assert p.max_hp == hp_expected
    for short, attr in ATTR_MAP.items():
        base_val = base[short]
        total = sum(table[lvl][f"{short}_plus"] for lvl in range(2, 12))
        total += table[11][f"{short}_plus"] * 2
        assert getattr(p, attr) == base_val + total
