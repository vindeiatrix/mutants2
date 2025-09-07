import contextlib
import datetime
import io
from pathlib import Path

from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.cli.shell import make_context
from mutants2.ui.theme import yellow


def run_commands(cmds, path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    persistence.SAVE_PATH = path / "save.json"
    w = world_mod.World(seeded_years={2000})
    p = Player(year=2000, clazz="Warrior")
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    ctx = make_context(p, w, save, dev=True)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        for c in cmds:
            ctx.dispatch_line(c)
    out = buf.getvalue()
    buf.close()
    return out, w, p


def test_debug_item_add_aliases_and_enchant(tmp_path):
    aliases = ["bug-skin", "bug skin armour", "bug-skin-armour", "bugskin"]
    for i, alias in enumerate(aliases):
        out, _, _ = run_commands(
            [f"debug item add {alias}", "get bug", "look bug", "inventory"],
            tmp_path / str(i),
        )
        assert "Unknown item" not in out
        assert "+1 Bug-Skin" in out
        assert "+1 Bug-Skin" not in out.split("inventory")[-1]


def test_look_and_convert_inventory(tmp_path):
    out, _, p = run_commands(
        [
            "debug item add bug-skin",
            "get bug",
            "look bug",
            "convert bug-skin",
            "inventory",
            "status",
        ],
        tmp_path / "inv",
    )
    assert "possesses a magical aura" in out
    assert yellow("The Bug-Skin vanishes with a flash!") in out
    assert yellow("You convert the Bug-Skin into 22100 ions.") in out
    inv_block = out.split("inventory")[-1].split("status")[0]
    assert "Bug-Skin" not in inv_block
    assert p.ions == 22100


def test_convert_worn_bug_skin(tmp_path):
    out, _, p = run_commands(
        [
            "debug item add bug-skin",
            "get bug",
            "wear bug",
            "convert bug",
            "inventory",
            "status",
        ],
        tmp_path / "worn",
    )
    assert yellow("The Bug-Skin vanishes with a flash!") in out
    assert yellow("You convert the Bug-Skin into 22100 ions.") in out
    inv_block = out.split("inventory")[-1].split("status")[0]
    assert "Bug-Skin" not in inv_block
    assert p.ions == 22100
