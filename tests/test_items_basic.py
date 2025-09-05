import os
from pathlib import Path
import subprocess
import sys

import json
import datetime

from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.ui.theme import white


def _ensure_profile(tmp_path):
    save_path = Path(tmp_path) / ".mutants2" / "save.json"
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
        p = Player(clazz="Warrior")
        w = World(seeded_years={2000})
        save = persistence.Save()
        save.last_topup_date = datetime.date.today().isoformat()
        save.last_class = "Warrior"
        save.profiles["Warrior"] = {
            "year": p.year,
            "positions": {
                str(y): {"x": x, "y": yy} for y, (x, yy) in p.positions.items()
            },
            "hp": p.hp,
            "max_hp": p.max_hp,
            "inventory": [],
            "ions": 0,
        }
        persistence.save(p, w, save)


def _run_game(commands, tmp_path):
    _ensure_profile(tmp_path)
    cmd = [sys.executable, "-m", "mutants2"]
    inp = "\n".join(commands) + "\n"
    return subprocess.run(
        cmd, input=inp, text=True, capture_output=True, env={"HOME": str(tmp_path)}
    )


def test_initial_spawn_approx_five_percent(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    persistence.SAVE_PATH = Path(tmp_path) / ".mutants2" / "save.json"
    p, ground, monsters, seeded, save = persistence.load()
    w = World(ground, seeded, monsters, global_seed=save.global_seed)
    w.year(p.year)
    count = sum(len(v) for (yr, _, _), v in w.ground.items() if yr == p.year)
    assert 360 <= count <= 440
    coords = {(x, y) for (yr, x, y) in w.ground if yr == p.year}
    assert len(coords) <= count


def test_pickup_and_drop_roundtrip(tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / ".mutants2" / "save.json"
    os.environ["HOME"] = str(tmp_path)
    p = Player()
    w = World({(2000, 0, 0): ["ion_decay"]}, {2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    result = _run_game(
        [
            "get Ion-Decay",
            "look",
            "inventory",
            "drop Ion-Decay",
            "look",
            "inventory",
            "exit",
        ],
        tmp_path,
    )
    out = result.stdout
    assert "You pick up Ion-Decay." in out
    assert white("Ion-Decay.") in out
    assert "You drop Ion-Decay." in out
    after = out.split("You drop Ion-Decay.")[-1]
    assert "On the ground lies:" in after and "Ion-Decay" in after
    assert "(empty)" in after


def test_inventory_rendering(tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / ".mutants2" / "save.json"
    os.environ["HOME"] = str(tmp_path)
    p = Player()
    p.inventory.extend(["ion_decay", "ion_decay", "gold_chunk"])
    w = World(seeded_years={2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    result = _run_game(["inventory", "exit"], tmp_path)
    assert white("Ion-Decay, Ion-Decay\u00a0(1), Gold-Chunk.") in result.stdout


def test_persistence_inventory_and_ground(tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / ".mutants2" / "save.json"
    os.environ["HOME"] = str(tmp_path)
    p = Player()
    w = World({(2000, 0, 0): ["ion_decay"]}, {2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    _run_game(["get Ion-Decay", "east", "exit"], tmp_path)
    result = _run_game(["inventory", "west", "look", "exit"], tmp_path)
    out = result.stdout
    assert white("Ion-Decay.") in out
    looked = out.split("look")[-1]
    assert "Ion-Decay" not in looked


def test_name_matching_case_insensitive(tmp_path):
    persistence.SAVE_PATH = Path(tmp_path) / ".mutants2" / "save.json"
    os.environ["HOME"] = str(tmp_path)
    p = Player()
    w = World({(2000, 0, 0): ["ion_decay"]}, {2000})
    save = persistence.Save()
    persistence.save(p, w, save)
    result = _run_game(
        ["get ion-decay", "drop ion-decay", "get Ion-Decay", "inventory", "exit"],
        tmp_path,
    )
    assert white("Ion-Decay.") in result.stdout
