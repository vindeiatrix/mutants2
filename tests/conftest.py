import os
import sys
import datetime
import json
from pathlib import Path

import pytest

# Ensure the package root is importable when tests run from within the tests directory
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def cli_runner(tmp_path):
    import subprocess
    from mutants2.engine import persistence, world as world_mod
    from mutants2.engine.player import Player

    class Runner:
        def run_commands(self, commands):
            cmd = [sys.executable, "-m", "mutants2"]
            env = os.environ.copy()
            env["HOME"] = str(tmp_path)
            persistence.SAVE_PATH = tmp_path / '.mutants2' / 'save.json'
            save_path = persistence.SAVE_PATH
            if save_path.exists():
                with open(save_path) as fh:
                    data = json.load(fh)
                if "profiles" not in data:
                    data["profiles"] = {}
                if "Warrior" not in data["profiles"]:
                    data["profiles"]["Warrior"] = {
                        "year": data.get("year", 2000),
                        "positions": data.get(
                            "positions", {str(2000): {"x": 0, "y": 0}}
                        ),
                        "hp": data.get("hp", 10),
                        "max_hp": data.get("max_hp", 10),
                        "inventory": data.get("inventory", {}),
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
                    "inventory": {},
                    "ions": p.ions,
                }
                persistence.save(p, w, save)
            inp = "\n".join(commands + ["exit"]) + "\n"
            result = subprocess.run(cmd, input=inp, text=True, capture_output=True, env=env)
            return result.stdout

    return Runner()
