import os
import pytest

from mutants2.engine import persistence
import re

from mutants2.engine.world import World
from mutants2.engine.player import Player


@pytest.fixture
def world_with_mutant_on_start(tmp_path):
    persistence.SAVE_PATH = tmp_path / ".mutants2" / "save.json"
    os.environ["HOME"] = str(tmp_path)
    p = Player()
    w = World(
        monsters={(2000, 0, 0): [{"key": "mutant", "hp": 3}]}, seeded_years={2000}
    )
    save = persistence.Save()
    persistence.save(p, w, save)
    return None


@pytest.fixture
def empty_start_world(tmp_path):
    persistence.SAVE_PATH = tmp_path / ".mutants2" / "save.json"
    os.environ["HOME"] = str(tmp_path)
    p = Player()
    w = World(seeded_years={2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    return None


def test_cannot_rest_in_danger(world_with_mutant_on_start, cli_runner):
    out = cli_runner.run_commands(["res"])
    assert "can’t rest" in out.lower()


def test_rest_heals_when_safe(empty_start_world, cli_runner):
    out = cli_runner.run_commands(["res"])
    assert "recover" in out


def test_status_shows_hp_and_coords(empty_start_world, cli_runner):
    out = cli_runner.run_commands(["sta"])
    assert "Hit Points" in out and "Year A.D." in out


def test_room_line_shows_monster_present(world_with_mutant_on_start, cli_runner):
    out = cli_runner.run_commands(["loo"])
    assert re.search(r"Mutant-\d{4}.*is here", out)
