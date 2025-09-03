import os
from pathlib import Path
import subprocess
import sys

from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player


def _run_game(commands, tmp_path):
    cmd = [sys.executable, '-m', 'mutants2']
    inp = '1\n' + '\n'.join(commands) + '\n'
    return subprocess.run(cmd, input=inp, text=True, capture_output=True, env={'HOME': str(tmp_path)})


def test_initial_spawn_approx_five_percent(tmp_path, monkeypatch):
    monkeypatch.setenv('HOME', str(tmp_path))
    persistence.SAVE_PATH = Path(tmp_path) / '.mutants2' / 'save.json'
    p, ground, monsters, seeded, save = persistence.load()
    w = World(ground, seeded, monsters, global_seed=save.global_seed)
    w.year(p.year)
    count = sum(1 for (yr, _, _), _ in w.ground.items() if yr == p.year)
    assert 25 <= count <= 60
    # Ensure one item per tile
    coords = {(x, y) for (yr, x, y) in w.ground if yr == p.year}
    assert len(coords) == count


def test_pickup_and_drop_roundtrip(tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    w = World({(2000, 0, 0): 'ion_decay'}, {2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    result = _run_game(['get Ion-Decay', 'look', 'inventory', 'drop Ion-Decay', 'look', 'inventory', 'exit'], tmp_path)
    out = result.stdout
    assert 'You pick up Ion-Decay.' in out
    assert 'Ion-Decay x1' in out
    assert 'You drop Ion-Decay.' in out
    after = out.split('You drop Ion-Decay.')[-1]
    assert 'On the ground lies:' in after and 'Ion-Decay' in after
    assert '(empty)' in after


def test_inventory_rendering(tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    p.inventory.update({'ion_decay': 2, 'gold_chunk': 1})
    w = World(seeded_years={2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    result = _run_game(['inventory', 'exit'], tmp_path)
    assert 'Ion-Decay x2' in result.stdout
    assert 'Gold-Chunk x1' in result.stdout


def test_persistence_inventory_and_ground(tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    w = World({(2000, 0, 0): 'ion_decay'}, {2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    _run_game(['get Ion-Decay', 'east', 'exit'], tmp_path)
    result = _run_game(['inventory', 'west', 'look', 'exit'], tmp_path)
    out = result.stdout
    assert 'Ion-Decay x1' in out
    assert 'On the ground lies:' not in out


def test_name_matching_case_insensitive(tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)
    p = Player()
    w = World({(2000, 0, 0): 'ion_decay'}, {2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    result = _run_game(['get ion-decay', 'drop ion-decay', 'get Ion-Decay', 'inventory', 'exit'], tmp_path)
    assert 'Ion-Decay x1' in result.stdout
