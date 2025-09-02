import os
import pytest

from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player


@pytest.fixture
def tile_with_item(tmp_path):
    persistence.SAVE_PATH = tmp_path / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    w = World({(2000, 0, 0): 'nuclear_thong'}, {2000})
    persistence.save(p, w)
    return None


@pytest.fixture
def inventory_with_item(tmp_path):
    persistence.SAVE_PATH = tmp_path / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    p.inventory['nuclear_thong'] = 1
    w = World(seeded_years={2000})
    persistence.save(p, w)
    return None


@pytest.fixture
def inventory_with_ion_items(tmp_path):
    persistence.SAVE_PATH = tmp_path / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    p.inventory.update({'ion_decay': 1, 'ion_pack': 1})
    w = World(seeded_years={2000})
    persistence.save(p, w)
    return None


def test_get_does_not_render(cli_runner, tile_with_item):
    out = cli_runner.run_commands(["look", "get nuc"])
    assert out.count("***") == 2
    assert "You pick up Nuclear-thong." in out


def test_drop_does_not_render(cli_runner, inventory_with_item):
    out = cli_runner.run_commands(["dro nuc"])
    assert out.count("***") == 1
    assert "You drop Nuclear-thong." in out


def test_item_prefix_ambiguous(cli_runner, inventory_with_ion_items):
    out = cli_runner.run_commands(["dro ion", "dro ion-dec"])
    assert "Ambiguous:" in out
    assert "You drop Ion-Decay" in out or "You drop Ion-Pack" in out


def test_abbrev_rules(cli_runner):
    assert "Unknown command" in cli_runner.run_commands(["i"])
    assert "***" in cli_runner.run_commands(["loo"])
    assert "Goodbye." in cli_runner.run_commands(["exi"])
    assert "Unknown command" in cli_runner.run_commands(["nor"])
    assert "***" in cli_runner.run_commands(["n"])


def test_travel_still_renders(cli_runner):
    out = cli_runner.run_commands(["tra 2100"])
    assert "***" in out and "0E" in out
