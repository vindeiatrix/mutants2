import pytest

from mutants2.engine import items
from mutants2.engine.player import Player

# mapping of item names to (weight_lbs, ion_value)
CAPTURE_SET = {
    "Bottle-Cap": (1, 22000),
    "Cheese": (1, 12000),
    "Cigarette-Butt": (1, 11000),
    "Ion-Booster": (10, 13000),
    "Ion-Decay": (10, 18000),
    "Ion-Pack": (50, 20000),
    "Gold-Chunk": (25, 25000),
    "Light-Spear": (10, 11000),
    "Nuclear-Decay": (50, 85000),
    "Nuclear-Rock": (10, 15000),
    "Nuclear-thong": (20, 13000),
    "Nuclear-Waste": (30, 15000),
}


@pytest.mark.parametrize("name,expected", CAPTURE_SET.items())
def test_catalog_has_correct_values(name, expected):
    item = items.find_by_name(name)
    assert item is not None
    weight, ion = expected
    assert item.weight_lbs == weight
    assert item.ion_value == ion


def test_inventory_weight_totals():
    p = Player()
    p.inventory.extend(["ion_decay", "ion_decay", "gold_chunk"])
    # weights: ion_decay=10*2=20, gold_chunk=25 -> total 45
    assert p.inventory_weight_lbs() == 45
