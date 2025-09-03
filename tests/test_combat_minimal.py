import os
import pytest

from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player
from pathlib import Path


@pytest.fixture
def world_with_mutant_on_start(tmp_path):
    persistence.SAVE_PATH = tmp_path / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    w = World(monsters={(2000, 0, 0): [{'key': 'mutant', 'hp': 3}]}, seeded_years={2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    return None


@pytest.fixture
def empty_start_world(tmp_path):
    persistence.SAVE_PATH = tmp_path / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    w = World(seeded_years={2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    return None


def test_attack_kills_with_few_hits(world_with_mutant_on_start, cli_runner):
    out = cli_runner.run_commands(["att", "att"])
    assert "You defeat the Mutant" in out


def test_retaliation_and_death_respawn(world_with_mutant_on_start, cli_runner):
    out = cli_runner.run_commands(["att"])
    assert "The Mutant hits you" in out
    # reset world with low player HP for death test
    save_path = Path(os.environ["HOME"]) / '.mutants2' / 'save.json'
    persistence.SAVE_PATH = save_path
    p = Player()
    p.max_hp = p.hp = 1
    w = World(monsters={(2000, 0, 0): [{'key': 'mutant', 'hp': 3}]}, seeded_years={2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    out2 = cli_runner.run_commands(["att", "att", "att", "att"])
    assert "You have died." in out2
    assert "Compass: (0E : 0N)" in out2


def test_cannot_rest_in_danger(world_with_mutant_on_start, cli_runner):
    out = cli_runner.run_commands(["res"])
    assert "can’t rest" in out.lower()


def test_rest_heals_when_safe(empty_start_world, cli_runner):
    out = cli_runner.run_commands(["res"])
    assert "recover" in out


def test_status_shows_hp_and_coords(empty_start_world, cli_runner):
    out = cli_runner.run_commands(["sta"])
    assert "HP:" in out and "Year:" in out


def test_room_line_shows_monster_present(world_with_mutant_on_start, cli_runner):
    out = cli_runner.run_commands(["loo"])
    assert "Mutant" in out and "is here" in out
