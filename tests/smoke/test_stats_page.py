import contextlib
import datetime
import io

from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.ui.theme import yellow, white


def test_stats_page(tmp_path):
    persistence.SAVE_PATH = tmp_path / "save.json"
    p = Player(year=2000, clazz="Warrior")
    p.inventory.extend(["ion_decay", "ion_decay", "gold_chunk"])
    w = world_mod.World(seeded_years={2000})
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ctx.dispatch_line("status")
    out = buf.getvalue()
    assert yellow("Name: Vindeiatrix / Mutant Warrior") in out
    assert yellow("Hit Points   : 40 / 40") in out
    assert yellow("Ions         : 0") in out
    assert yellow("Year A.D.     : 2000") in out
    assert (
        yellow("You are carrying the following items:  (Total Weight: 45 LB's)") in out
    )
    assert white("Ion-Decay, Ion-Decay\u00a0(1), Gold-Chunk.") in out
