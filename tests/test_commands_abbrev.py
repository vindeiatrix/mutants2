import pytest

from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player


@pytest.fixture
def seeded_world_with_item(tmp_path):
    persistence.SAVE_PATH = tmp_path / '.mutants2' / 'save.json'
    w = World({(2000, 0, 0): 'ion_decay'}, {2000})
    p = Player()
    persistence.save(p, w)
    return None


def test_travel_auto_renders(cli_runner):
    out = cli_runner.run_commands(["look", "tra 2100"])
    assert "***" in out and "0E" in out


def test_three_letter_abbrevs(cli_runner):
    out = cli_runner.run_commands(["loo"])
    assert "***" in out
    out = cli_runner.run_commands(["cla", "back"])
    assert "Class" in out
    out = cli_runner.run_commands(["las"])
    assert "***" in out
    out = cli_runner.run_commands(["exi"])
    assert "Goodbye." in out


def test_inventory_aliases(cli_runner):
    out = cli_runner.run_commands(["inv"])
    assert "(empty)" in out or "Inventory" in out
    out = cli_runner.run_commands(["i"])
    assert "Unknown command" in out


def test_get_drop_abbrevs(cli_runner, seeded_world_with_item):
    out = cli_runner.run_commands(["tak Ion-Decay", "inv"])
    assert "Ion-Decay" in out
    out = cli_runner.run_commands(["dro Ion-Decay", "look"])
    assert "Ion-Decay" in out or "On the ground lies" in out


def test_directions_one_letter_only(cli_runner):
    out = cli_runner.run_commands(["nor"])
    assert "Unknown command" in out
    out = cli_runner.run_commands(["sou"])
    assert "Unknown command" in out
    out = cli_runner.run_commands(["n"])
    assert "***" in out
    out = cli_runner.run_commands(["north"])
    assert "***" in out
