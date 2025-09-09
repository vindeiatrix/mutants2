import os
import subprocess
import sys
from io import StringIO
import contextlib
import json
import datetime

import pytest

from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.engine.render import render_room_view


def render_output(w: World, p: Player) -> str:
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        render_room_view(p, w)
    return buf.getvalue()


def test_spawn_deterministic():
    w1 = World(global_seed=123)
    w2 = World(global_seed=123)
    w1.year(2000)
    w2.year(2000)
    assert w1.monsters_in_year(2000) == w2.monsters_in_year(2000)


def _clear_monsters(w: World, year: int = 2000):
    for (x, y), _ in list(w.monsters_in_year(year).items()):
        w.remove_monster(year, x, y)


def test_nearest_monster_cues():
    w = World()
    w.year(2000)
    _clear_monsters(w)
    w.place_monster(2000, 1, 0, "mutant")
    p = Player()
    out = render_output(w, p)
    assert "shadows to the east" in out.lower()


def test_no_cues_when_none_near():
    w = World()
    w.year(2000)
    _clear_monsters(w)
    p = Player()
    out = render_output(w, p)
    assert "shadows to" not in out.lower()


@pytest.fixture
def cli_runner_dev(tmp_path):
    from mutants2.engine import persistence, world as world_mod
    from mutants2.engine.player import Player

    class Runner:
        def run_commands(self, commands):
            cmd = [sys.executable, "-m", "mutants2"]
            env = os.environ.copy()
            env["HOME"] = str(tmp_path)
            env["MUTANTS2_DEV"] = "1"
            persistence.SAVE_PATH = tmp_path / ".mutants2" / "save.json"
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
                        "inventory": data.get("inventory", []),
                        "ions": data.get("ions", 0),
                    }
                data["last_class"] = "Warrior"
                with open(save_path, "w") as fh:
                    json.dump(data, fh)
            else:
                p = Player(clazz="Warrior")
                w = world_mod.World(seeded_years={2000})
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
            inp = "\n".join(commands + ["exit"]) + "\n"
            result = subprocess.run(
                cmd, input=inp, text=True, capture_output=True, env=env
            )
            return result.stdout

    return Runner()


def test_dev_spawn_here(cli_runner_dev):
    out = cli_runner_dev.run_commands(["debug mon here"])
    assert "spawned monster" in out.lower()
    out2 = cli_runner_dev.run_commands(["debug mon here"])
    assert "removed monster" in out2.lower()
