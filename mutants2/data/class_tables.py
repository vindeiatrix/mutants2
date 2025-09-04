from __future__ import annotations

# Level 1 base stats for each class
BASE_LEVEL1 = {
    "thief": {"str": 15, "int": 9, "wis": 8, "dex": 14, "con": 15, "cha": 16, "hp": 18, "ac": 1},
    "priest": {"str": 20, "int": 12, "wis": 13, "dex": 17, "con": 17, "cha": 14, "hp": 30, "ac": 1},
    "wizard": {"str": 14, "int": 17, "wis": 17, "dex": 13, "con": 14, "cha": 15, "hp": 23, "ac": 1},
    "warrior": {"str": 23, "int": 12, "wis": 14, "dex": 20, "con": 19, "cha": 9, "hp": 40, "ac": 2},
    "mage": {"str": 18, "int": 23, "wis": 20, "dex": 16, "con": 15, "cha": 20, "hp": 28, "ac": 1},
}

# Per-level progression tables.
PROGRESSION = {
    "thief": {
        2: {"xp_to_reach": 30_000, "hp_plus": 3, "str_plus": 2, "int_plus": 2, "wis_plus": 2, "dex_plus": 2, "con_plus": 3, "cha_plus": 2},
        3: {"xp_to_reach": 100_000, "hp_plus": 3, "str_plus": 2, "int_plus": 3, "wis_plus": 2, "dex_plus": 3, "con_plus": 3, "cha_plus": 2},
        4: {"xp_to_reach": 210_000, "hp_plus": 4, "str_plus": 3, "int_plus": 3, "wis_plus": 2, "dex_plus": 4, "con_plus": 4, "cha_plus": 2},
        5: {"xp_to_reach": 340_000, "hp_plus": 5, "str_plus": 3, "int_plus": 3, "wis_plus": 2, "dex_plus": 5, "con_plus": 4, "cha_plus": 2},
        6: {"xp_to_reach": 540_000, "hp_plus": 6, "str_plus": 3, "int_plus": 4, "wis_plus": 2, "dex_plus": 6, "con_plus": 6, "cha_plus": 2},
        7: {"xp_to_reach": 700_000, "hp_plus": 7, "str_plus": 4, "int_plus": 4, "wis_plus": 3, "dex_plus": 7, "con_plus": 7, "cha_plus": 3},
        8: {"xp_to_reach": 930_000, "hp_plus": 8, "str_plus": 4, "int_plus": 4, "wis_plus": 3, "dex_plus": 8, "con_plus": 7, "cha_plus": 3},
        9: {"xp_to_reach": 1_900_000, "hp_plus": 8, "str_plus": 4, "int_plus": 4, "wis_plus": 3, "dex_plus": 9, "con_plus": 8, "cha_plus": 3},
        10:{"xp_to_reach": 2_400_000, "hp_plus": 8, "str_plus": 5, "int_plus": 4, "wis_plus": 3, "dex_plus": 10, "con_plus": 8, "cha_plus": 3},
        11:{"xp_to_reach": 3_300_000, "hp_plus": 9, "str_plus": 6, "int_plus": 5, "wis_plus": 4, "dex_plus": 11, "con_plus": 9, "cha_plus": 4},
    },
    "priest": {
        2: {"xp_to_reach": 40_000, "hp_plus": 1, "str_plus": 1, "int_plus": 1, "wis_plus": 1, "dex_plus": 4, "con_plus": 2, "cha_plus": 2},
        3: {"xp_to_reach": 80_000, "hp_plus": 2, "str_plus": 1, "int_plus": 1, "wis_plus": 1, "dex_plus": 4, "con_plus": 2, "cha_plus": 2},
        4: {"xp_to_reach": 170_000, "hp_plus": 3, "str_plus": 2, "int_plus": 1, "wis_plus": 3, "dex_plus": 5, "con_plus": 2, "cha_plus": 3},
        5: {"xp_to_reach": 290_000, "hp_plus": 3, "str_plus": 3, "int_plus": 2, "wis_plus": 3, "dex_plus": 5, "con_plus": 2, "cha_plus": 4},
        6: {"xp_to_reach": 410_000, "hp_plus": 3, "str_plus": 3, "int_plus": 2, "wis_plus": 4, "dex_plus": 6, "con_plus": 2, "cha_plus": 5},
        7: {"xp_to_reach": 650_000, "hp_plus": 3, "str_plus": 3, "int_plus": 2, "wis_plus": 4, "dex_plus": 6, "con_plus": 3, "cha_plus": 6},
        8: {"xp_to_reach": 890_000, "hp_plus": 3, "str_plus": 4, "int_plus": 3, "wis_plus": 5, "dex_plus": 6, "con_plus": 3, "cha_plus": 7},
        9: {"xp_to_reach": 1_100_000, "hp_plus": 4, "str_plus": 4, "int_plus": 3, "wis_plus": 5, "dex_plus": 7, "con_plus": 3, "cha_plus": 8},
        10:{"xp_to_reach": 2_300_000, "hp_plus": 4, "str_plus": 5, "int_plus": 3, "wis_plus": 6, "dex_plus": 7, "con_plus": 3, "cha_plus": 8},
        11:{"xp_to_reach": 5_400_000, "hp_plus": 5, "str_plus": 5, "int_plus": 4, "wis_plus": 6, "dex_plus": 7, "con_plus": 3, "cha_plus": 8},
    },
    "wizard": {
        2: {"xp_to_reach": 40_000, "hp_plus": 1, "str_plus": 1, "int_plus": 3, "wis_plus": 2, "dex_plus": 1, "con_plus": 1, "cha_plus": 5},
        3: {"xp_to_reach": 90_000, "hp_plus": 2, "str_plus": 1, "int_plus": 3, "wis_plus": 2, "dex_plus": 1, "con_plus": 1, "cha_plus": 6},
        4: {"xp_to_reach": 190_000, "hp_plus": 2, "str_plus": 1, "int_plus": 4, "wis_plus": 3, "dex_plus": 1, "con_plus": 1, "cha_plus": 7},
        5: {"xp_to_reach": 310_000, "hp_plus": 2, "str_plus": 2, "int_plus": 5, "wis_plus": 3, "dex_plus": 2, "con_plus": 2, "cha_plus": 8},
        6: {"xp_to_reach": 560_000, "hp_plus": 3, "str_plus": 2, "int_plus": 6, "wis_plus": 4, "dex_plus": 2, "con_plus": 2, "cha_plus": 9},
        7: {"xp_to_reach": 780_000, "hp_plus": 3, "str_plus": 2, "int_plus": 6, "wis_plus": 4, "dex_plus": 2, "con_plus": 2, "cha_plus": 9},
        8: {"xp_to_reach": 1_300_000, "hp_plus": 3, "str_plus": 2, "int_plus": 6, "wis_plus": 5, "dex_plus": 2, "con_plus": 2, "cha_plus": 9},
        9: {"xp_to_reach": 2_100_000, "hp_plus": 4, "str_plus": 2, "int_plus": 7, "wis_plus": 5, "dex_plus": 2, "con_plus": 3, "cha_plus": 9},
        10:{"xp_to_reach": 3_350_000, "hp_plus": 4, "str_plus": 2, "int_plus": 7, "wis_plus": 6, "dex_plus": 3, "con_plus": 3, "cha_plus": 10},
        11:{"xp_to_reach": 4_800_000, "hp_plus": 4, "str_plus": 2, "int_plus": 7, "wis_plus": 7, "dex_plus": 3, "con_plus": 3, "cha_plus": 11},
    },
    "warrior": {
        2: {"xp_to_reach": 50_000, "hp_plus": 4, "str_plus": 8, "int_plus": 1, "wis_plus": 1, "dex_plus": 3, "con_plus": 3, "cha_plus": 1},
        3: {"xp_to_reach": 130_000, "hp_plus": 5, "str_plus": 8, "int_plus": 1, "wis_plus": 1, "dex_plus": 5, "con_plus": 4, "cha_plus": 1},
        4: {"xp_to_reach": 320_000, "hp_plus": 5, "str_plus": 9, "int_plus": 1, "wis_plus": 1, "dex_plus": 7, "con_plus": 6, "cha_plus": 1},
        5: {"xp_to_reach": 510_000, "hp_plus": 6, "str_plus": 10, "int_plus": 1, "wis_plus": 1, "dex_plus": 8, "con_plus": 8, "cha_plus": 1},
        6: {"xp_to_reach": 860_000, "hp_plus": 7, "str_plus": 12, "int_plus": 1, "wis_plus": 1, "dex_plus": 10, "con_plus": 11, "cha_plus": 1},
        7: {"xp_to_reach": 1_150_000, "hp_plus": 8, "str_plus": 15, "int_plus": 1, "wis_plus": 1, "dex_plus": 12, "con_plus": 13, "cha_plus": 1},
        8: {"xp_to_reach": 2_100_000, "hp_plus": 8, "str_plus": 18, "int_plus": 1, "wis_plus": 1, "dex_plus": 12, "con_plus": 15, "cha_plus": 1},
        9: {"xp_to_reach": 3_250_000, "hp_plus": 10, "str_plus": 20, "int_plus": 1, "wis_plus": 1, "dex_plus": 15, "con_plus": 18, "cha_plus": 1},
        10:{"xp_to_reach": 4_990_000, "hp_plus": 10, "str_plus": 22, "int_plus": 1, "wis_plus": 1, "dex_plus": 18, "con_plus": 20, "cha_plus": 1},
        11:{"xp_to_reach": 5_400_000, "hp_plus": 11, "str_plus": 25, "int_plus": 1, "wis_plus": 1, "dex_plus": 20, "con_plus": 20, "cha_plus": 1},
    },
    "mage": {
        2: {"xp_to_reach": 40_000, "hp_plus": 2, "str_plus": 3, "int_plus": 6, "wis_plus": 5, "dex_plus": 1, "con_plus": 2, "cha_plus": 3},
        3: {"xp_to_reach": 90_000, "hp_plus": 3, "str_plus": 3, "int_plus": 6, "wis_plus": 6, "dex_plus": 2, "con_plus": 3, "cha_plus": 3},
        4: {"xp_to_reach": 400_000, "hp_plus": 4, "str_plus": 3, "int_plus": 7, "wis_plus": 6, "dex_plus": 3, "con_plus": 4, "cha_plus": 4},
        5: {"xp_to_reach": 1_120_000, "hp_plus": 5, "str_plus": 4, "int_plus": 7, "wis_plus": 7, "dex_plus": 3, "con_plus": 4, "cha_plus": 4},
        6: {"xp_to_reach": 1_650_000, "hp_plus": 6, "str_plus": 4, "int_plus": 8, "wis_plus": 7, "dex_plus": 3, "con_plus": 4, "cha_plus": 5},
        7: {"xp_to_reach": 2_400_000, "hp_plus": 6, "str_plus": 4, "int_plus": 8, "wis_plus": 8, "dex_plus": 4, "con_plus": 5, "cha_plus": 5},
        8: {"xp_to_reach": 3_250_000, "hp_plus": 6, "str_plus": 4, "int_plus": 8, "wis_plus": 8, "dex_plus": 5, "con_plus": 5, "cha_plus": 5},
        9: {"xp_to_reach": 4_000_000, "hp_plus": 6, "str_plus": 4, "int_plus": 9, "wis_plus": 9, "dex_plus": 5, "con_plus": 5, "cha_plus": 5},
        10:{"xp_to_reach": 5_200_000, "hp_plus": 7, "str_plus": 4, "int_plus": 9, "wis_plus": 9, "dex_plus": 5, "con_plus": 5, "cha_plus": 6},
        11:{"xp_to_reach": 6_000_000, "hp_plus": 7, "str_plus": 5, "int_plus": 9, "wis_plus": 10, "dex_plus": 5, "con_plus": 6, "cha_plus": 7},
    },
}
