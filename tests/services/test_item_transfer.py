import pytest
from mutants.services import item_transfer

@pytest.mark.parametrize("field", ["armor", "armour"])
def test_equipped_armor_protected(field):
    # simulate a player state with armor/armour equipped
    player = {field: {"iid": "armor_001"}}
    assert item_transfer._armor_iid(player) == "armor_001"
