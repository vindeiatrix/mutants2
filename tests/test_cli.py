import subprocess
import os
import subprocess
import sys
import json
import datetime
from pathlib import Path

from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player


def _ensure_profile(tmp_path):
    save_path = Path(tmp_path) / '.mutants2' / 'save.json'
    persistence.SAVE_PATH = save_path
    if save_path.exists():
        with open(save_path) as fh:
            data = json.load(fh)
        if "profiles" not in data:
            data["profiles"] = {}
        if "Warrior" not in data["profiles"]:
            data["profiles"]["Warrior"] = {
                "year": data.get("year", 2000),
                "positions": data.get("positions", {str(2000): {"x": 0, "y": 0}}),
                "hp": data.get("hp", 10),
                "max_hp": data.get("max_hp", 10),
                "inventory": data.get("inventory", []),
                "ions": data.get("ions", 0),
            }
        data["last_class"] = "Warrior"
        with open(save_path, "w") as fh:
            json.dump(data, fh)
    else:
        p = Player(clazz="Warrior", ions=100000)
        w = world_mod.World(seeded_years={2000})
        save = persistence.Save()
        save.last_topup_date = datetime.date.today().isoformat()
        save.last_class = "Warrior"
        save.profiles["Warrior"] = {
            "year": p.year,
            "positions": {str(y): {"x": x, "y": yy} for y, (x, yy) in p.positions.items()},
            "hp": p.hp,
            "max_hp": p.max_hp,
            "inventory": [],
            "ions": p.ions,
        }
        persistence.save(p, w, save)


def test_cli_smoke(tmp_path):
    _ensure_profile(tmp_path)
    cmd = [sys.executable, '-m', 'mutants2']
    inp = 'look\nnorth\nlast\ntravel 2100\nlook\nexit\n'
    result = subprocess.run(cmd, input=inp, text=True, capture_output=True, env={'HOME': str(tmp_path)})
    assert result.returncode == 0
    assert 'Compass:' in result.stdout


def _run_game(commands, tmp_path):
    _ensure_profile(tmp_path)
    cmd = [sys.executable, '-m', 'mutants2']
    inp = '\n'.join(commands) + '\n'
    return subprocess.run(cmd, input=inp, text=True, capture_output=True, env={'HOME': str(tmp_path)})


def test_move_shows_room_after_success(tmp_path):
    result = _run_game(['east', 'exit'], tmp_path)
    assert result.returncode == 0
    # Initial render plus post-move render
    assert result.stdout.count('***') >= 2
    assert 'Compass: (1E : 0N)' in result.stdout


def test_blocked_move_suppresses_room(tmp_path):
    cmds = ['west'] * 16 + ['exit']
    result = _run_game(cmds, tmp_path)
    assert result.returncode == 0
    assert "struck back" in result.stdout.lower()
    lines = result.stdout.splitlines()
    sb_idx = max(i for i, line in enumerate(lines) if "struck back" in line.lower())
    after = []
    for line in lines[sb_idx + 1:]:
        if line.strip().lower() == 'exit' or line.strip() == 'Goodbye.':
            break
        after.append(line)
    forbidden = ('Room:', 'Compass:', 'Exits:', 'Ground:', 'Presence:', 'Shadows:', '***')
    for line in after:
        assert not any(tok in line for tok in forbidden)


def test_direction_aliases_one_letter(tmp_path):
    result = _run_game(['n', 's', 'e', 'w', 'exit'], tmp_path)
    assert result.returncode == 0
    # One render per command plus initial
    assert result.stdout.count('***') >= 5
    assert 'Compass: (0E : 1N)' in result.stdout
    assert 'Compass: (1E : 0N)' in result.stdout


def test_history_file_created_non_tty_safe(tmp_path):
    result = _run_game(['look', 'exit'], tmp_path)
    assert result.returncode == 0
    histfile = tmp_path / '.mutants2' / 'history'
    assert histfile.exists()
