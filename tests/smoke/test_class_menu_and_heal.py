import subprocess
import subprocess
import sys
import contextlib
import io
import re
import tempfile
from pathlib import Path

from mutants2.cli.shell import make_context
from mutants2.engine import world as world_mod, persistence
from mutants2.engine.player import Player


def run_cli(inp: str, home, env_extra=None):
    cmd = [sys.executable, '-m', 'mutants2']
    env = {'HOME': str(home)}
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


def test_class_menu_order_and_info(tmp_path):
    result = run_cli('exit\n', tmp_path)
    out = result.stdout
    lines = [line for line in out.splitlines() if line and line[0].isdigit()]
    assert lines == [
        "1. Mutant Thief    Level: 1   Year: 2000   (0 0)",
        "2. Mutant Priest    Level: 1   Year: 2000   (0 0)",
        "3. Mutant Wizard    Level: 1   Year: 2000   (0 0)",
        "4. Mutant Warrior    Level: 1   Year: 2000   (0 0)",
        "5. Mutant Mage    Level: 1   Year: 2000   (0 0)",
    ]


def test_heal_below_max():
    out, p = run_heal('hea', hp=10, max_hp=20, ions=2000)
    assert "Your body glows as it heals 3 points!" in out
    assert p.hp == 13
    assert p.ions == 1000


def test_heal_to_max():
    out, p = run_heal('heal', hp=19, max_hp=20, ions=3000)
    assert "Your body glows as it heals 3 points!" in out
    assert "You're healed to the maximum!" in out
    assert p.hp == 20
    assert p.ions == 2000


def test_heal_already_max():
    out, p = run_heal('heal', hp=20, max_hp=20, ions=5000)
    assert "Nothing happens!" in out
    assert p.hp == 20
    assert p.ions == 5000


def test_heal_insufficient_ions():
    out, p = run_heal('heal', hp=10, max_hp=20, ions=500)
    assert "Nothing happens!" in out
    assert p.hp == 10
    assert p.ions == 500
