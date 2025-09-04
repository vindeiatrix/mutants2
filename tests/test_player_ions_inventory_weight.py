import os
from pathlib import Path

from mutants2.engine import persistence
from mutants2.engine.player import Player
from mutants2.engine.world import World
from mutants2.ui.theme import yellow, cyan


def test_inventory_weight_and_stats(cli_runner, tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / '.mutants2' / 'save.json'
    os.environ['HOME'] = str(tmp_path)

    p = Player()
    p.inventory.update({'ion_decay': 2, 'gold_chunk': 1})
    w = World(seeded_years={2000})
    save = persistence.Save()
    persistence.save(p, w, save)

    out = cli_runner.run_commands(['inventory', 'status'])

    # Inventory header and weight
    assert yellow("You are carrying the following items: (Total Weight: 45 LB's)") in out
    assert cyan('Ion-Decay, Ion-Decay, Gold-Chunk.') in out

    # Stats page ions
    assert 'Total Ions: 0' in out

