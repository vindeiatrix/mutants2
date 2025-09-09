import contextlib
import io
import tempfile
from pathlib import Path

from mutants2.cli.shell import make_context
from mutants2.engine import world as world_mod, persistence
from mutants2.engine.player import Player
from mutants2.ui.theme import COLOR_HEADER, COLOR_ITEM


def run_status() -> list[str]:
    save = persistence.Save(global_seed=42)
    w = world_mod.World(global_seed=42)
    w.year(2000)
    inventory = [{"key": "skull"}, {"key": "ion_pack"}]
    p = Player(year=2000, clazz="Warrior", ions=100000, inventory=inventory)
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            ctx.dispatch_line("status")
    return buf.getvalue().splitlines()


def test_stats_inventory_color() -> None:
    lines = run_status()
    header = COLOR_HEADER(
        "You are carrying the following items:  (Total Weight: 55 LB's)"
    )
    idx = lines.index(header)
    assert lines[idx + 1] == COLOR_HEADER("Skull, Ion-Pack.")

    ion_line = next(ln for ln in lines if "Ions" in ln)
    label = COLOR_ITEM("Ions         :")
    assert ion_line.startswith(label)
    assert "\x1b[" not in ion_line.replace(label, "")
