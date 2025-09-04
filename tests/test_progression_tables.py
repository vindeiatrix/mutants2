import json
import pytest

from mutants2.engine.player import Player
from mutants2.engine import leveling, persistence
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
    assert p.ac == base["ac"]
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
    hp_expected = base["hp"] + sum(table[l]["hp_plus"] for l in range(2, target + 1))
    assert p.max_hp == hp_expected
    for short, attr in ATTR_MAP.items():
        expected = base[short] + sum(table[l][f"{short}_plus"] for l in range(2, target + 1))
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
    hp_expected = base["hp"] + sum(table[l]["hp_plus"] for l in range(2, 12)) + table[11]["hp_plus"] * 2
    assert p.max_hp == hp_expected
    for short, attr in ATTR_MAP.items():
        base_val = base[short]
        total = sum(table[l][f"{short}_plus"] for l in range(2, 12))
        total += table[11][f"{short}_plus"] * 2
        assert getattr(p, attr) == base_val + total


def test_migration_recomputes_stats(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    persistence.SAVE_PATH = tmp_path / ".mutants2" / "save.json"
    table = PROGRESSION["warrior"]
    save_data = {
        "profiles": {
            "warrior": {
                "year": 2000,
                "positions": {"2000": {"x": 0, "y": 0}},
                "inventory": {},
                "hp": 9999,
                "max_hp": 9999,
                "ions": 0,
                "level": 3,
                "exp": table[3]["xp_to_reach"],
                "strength": 0,
                "intelligence": 0,
                "wisdom": 0,
                "dexterity": 0,
                "constitution": 0,
                "charisma": 0,
                "ac": 0,
            }
        },
        "last_class": "warrior",
    }
    persistence.SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(persistence.SAVE_PATH, "w") as fh:
        json.dump(save_data, fh)
    player, _, _, _, save_meta = persistence.load()
    base = BASE_LEVEL1["warrior"]
    table = PROGRESSION["warrior"]
    assert player.level == 3
    hp_expected = base["hp"] + table[2]["hp_plus"] + table[3]["hp_plus"]
    assert player.max_hp == hp_expected
    assert player.hp == hp_expected
    str_expected = base["str"] + table[2]["str_plus"] + table[3]["str_plus"]
    assert player.strength == str_expected
    assert save_meta.profiles["warrior"].tables_migrated is True
