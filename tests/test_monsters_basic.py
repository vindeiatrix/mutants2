import os
import subprocess
import sys
from io import StringIO
import contextlib

import pytest

import os
import subprocess
import sys
from io import StringIO
import contextlib

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
    assert "shadow flickers to the east" in out.lower()


def test_no_cues_when_none_near():
    w = World()
    w.year(2000)
    _clear_monsters(w)
    p = Player()
    out = render_output(w, p)
    assert "shadow flickers" not in out.lower()


@pytest.fixture
def cli_runner_dev(tmp_path):
    class Runner:
        def run_commands(self, commands):
            cmd = [sys.executable, "-m", "mutants2"]
            env = os.environ.copy()
            env["HOME"] = str(tmp_path)
            env["MUTANTS2_DEV"] = "1"
            inp = "1\n" + "\n".join(commands + ["exit"]) + "\n"
            result = subprocess.run(cmd, input=inp, text=True, capture_output=True, env=env)
            return result.stdout
    return Runner()


def test_dev_spawn_here(cli_runner_dev):
    out = cli_runner_dev.run_commands(["debug mon here"])
    assert "spawned monster" in out.lower()
    out2 = cli_runner_dev.run_commands(["debug mon here"])
    assert "removed monster" in out2.lower()
