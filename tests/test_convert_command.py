import datetime
import os

import pytest

from mutants2.engine import persistence
from mutants2.engine.player import Player
from mutants2.engine.world import World
from mutants2.ui.theme import yellow


@pytest.fixture
def inventory_with_cap(tmp_path):
    persistence.SAVE_PATH = tmp_path / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    p.inventory['bottle_cap'] = 1
    w = World(seeded_years={2000})
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    persistence.save(p, w, save)
    return None


def test_convert_bottle_cap(cli_runner, inventory_with_cap):
    out = cli_runner.run_commands(["convert b", "inventory", "status"])
    assert out.count("***") == 2
    assert yellow("The Bottle-Cap vanishes with a flash!") in out
    assert yellow("You convert the Bottle-Cap into 22,000 ions.") in out
    assert "(empty)" in out
    assert "Ions         : 22000" in out
