import subprocess
import sys
import contextlib
import io
import re
import tempfile
from pathlib import Path

from mutants2.cli.shell import make_context
from mutants2.engine import world as world_mod, persistence, items
from mutants2.engine.player import Player


def run_cli(inp: str, home, env_extra=None):
    cmd = [sys.executable, "-m", "mutants2"]
    env = {"HOME": str(home)}
    if env_extra:
        env.update(env_extra)
    return subprocess.run(cmd, input=inp, text=True, capture_output=True, env=env)


def run_heal(cmd: str, *, hp: int, max_hp: int, ions: int):
    save = persistence.Save(global_seed=42)
    w = world_mod.World(global_seed=42)
    w.year(2000)
    p = Player(year=2000, clazz="Warrior", hp=hp, max_hp=max_hp, ions=ions)
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            ctx.dispatch_line(cmd)
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    buf.close()
    return out, p


def run_debug(cmd: str, setup=None):
    save = persistence.Save(global_seed=42)
    w = world_mod.World(global_seed=42)
    w.year(2000)
    p = Player(year=2000, clazz="Warrior")
    if setup:
        setup(w, p)
    ctx = make_context(p, w, save, dev=True)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            ctx.dispatch_line(cmd)
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    buf.close()
    return out, w, p


def test_class_menu_alignment(tmp_path):
    result = run_cli("exit\n", tmp_path)
    out = result.stdout
    lines = [
        line for line in out.splitlines() if line.strip() and line.strip()[0].isdigit()
    ]
    assert lines == [
        " 1. Mutant Thief    Level:  1   Year: 2000  ( 0   0)",
        " 2. Mutant Priest   Level:  1   Year: 2000  ( 0   0)",
        " 3. Mutant Wizard   Level:  1   Year: 2000  ( 0   0)",
        " 4. Mutant Warrior  Level:  1   Year: 2000  ( 0   0)",
        " 5. Mutant Mage     Level:  1   Year: 2000  ( 0   0)",
    ]


def test_heal_insufficient_ions():
    out, p = run_heal("heal", hp=10, max_hp=20, ions=900)
    assert "You don't have enough ions to heal!" in out
    assert p.hp == 10
    assert p.ions == 900


def test_heal_below_max():
    out, p = run_heal("heal", hp=10, max_hp=20, ions=2000)
    assert "Your body glows as it heals 3 points!" in out
    assert p.hp == 13
    assert p.ions == 1000


def test_heal_to_max():
    out, p = run_heal("heal", hp=19, max_hp=20, ions=3000)
    assert "You're healed to the maximum!" in out
    assert p.hp == 20
    assert p.ions == 2000


def test_heal_already_max():
    out, p = run_heal("heal", hp=20, max_hp=20, ions=5000)
    assert "Nothing happens!" in out
    assert p.hp == 20
    assert p.ions == 5000


def test_debug_mon_clear():
    def setup(w, p):
        w._monsters = {k: v for k, v in w.monsters.items() if k[0] != p.year}
        for _ in range(3):
            w.place_monster(p.year, p.x, p.y, "mutant")

    out, w, p = run_debug("debug mon clear", setup=setup)
    lines = [line for line in out.splitlines() if line]
    assert lines[-1] == "Cleared 3 monster(s) in this room."
    assert not w.has_monster(p.year, p.x, p.y)


def test_debug_mon_clear_year():
    def setup(w, p):
        w._monsters = {k: v for k, v in w.monsters.items() if k[0] != p.year}
        w.place_monster(p.year, 1, 1, "mutant")
        w.place_monster(p.year, 2, 2, "mutant")
        w.place_monster(p.year, 2, 2, "mutant")

    out, w, p = run_debug("debug mon clear year", setup=setup)
    lines = [line for line in out.splitlines() if line]
    assert lines[-1].endswith(f"in year {p.year}.")
    assert w.monster_count(p.year) == 0


def test_debug_item_and_mon_count():
    def setup_items(w, p):
        w.ground = {k: v for k, v in w.ground.items() if k[0] != p.year}
        w.add_ground_item(p.year, p.x, p.y, items.SPAWNABLE_KEYS[0])
        w.add_ground_item(p.year, p.x, p.y + 1, items.SPAWNABLE_KEYS[1])

    out, w, p = run_debug("debug item count", setup=setup_items)
    lines = [line for line in out.splitlines() if line]
    assert lines[-1] == f"Items on ground in year {p.year}: 2"

    def setup_mon(w, p):
        w._monsters = {k: v for k, v in w.monsters.items() if k[0] != p.year}
        w.place_monster(p.year, p.x, p.y, "mutant")
        w.place_monster(p.year, p.x + 1, p.y, "mutant")

    out2, w2, p2 = run_debug("debug mon count", setup=setup_mon)
    lines2 = [line for line in out2.splitlines() if line]
    assert lines2[-1] == f"Monsters in year {p2.year}: 2"
