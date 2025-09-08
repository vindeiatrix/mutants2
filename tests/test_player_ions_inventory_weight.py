import os
from pathlib import Path

from mutants2.engine import persistence
from mutants2.engine.player import Player
from mutants2.engine.world import World
from mutants2.ui.theme import COLOR_HEADER, COLOR_ITEM, white


def test_inventory_weight_and_stats(cli_runner, tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / ".mutants2" / "save.json"
    os.environ["HOME"] = str(tmp_path)

    p = Player()
    p.inventory.extend(["ion_decay", "ion_decay", "gold_chunk"])
    w = World(seeded_years={2000})
    save = persistence.Save()
    persistence.save(p, w, save)

    out = cli_runner.run_commands(["inventory", "status"])

    # Inventory header and weight
    assert (
        COLOR_HEADER("You are carrying the following items: (Total Weight: 45 LB's)")
        in out
    )
    assert white("Ion-Decay, Ion-Decay\u00a0(1), Gold-Chunk.") in out

    # Stats page ions
    assert f"{COLOR_ITEM('Ions         :')} 30000" in out
