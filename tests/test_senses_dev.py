import os

import pytest


def enable_dev_env():
    os.environ["MUTANTS2_DEV"] = "1"


@pytest.fixture
def cli_runner(tmp_path):
    import subprocess, sys

    class Runner:
        def run_commands(self, commands):
            cmd = [sys.executable, "-m", "mutants2"]
            env = os.environ.copy()
            env.setdefault("HOME", str(tmp_path))
            inp = "back\n" + "\n".join(commands + ["exit"]) + "\n"
            result = subprocess.run(cmd, input=inp, text=True, capture_output=True, env=env)
            return result.stdout

    return Runner()


def test_debug_commands_rejected_without_dev(cli_runner):
    os.environ.pop("MUTANTS2_DEV", None)
    out = cli_runner.run_commands(["debug shadow north", "look"])
    assert "Debug commands are available only in dev mode." in out


def test_shadow_and_footsteps_render_once(cli_runner):
    enable_dev_env()
    out = cli_runner.run_commands([
        "debug clear",
        "debug shadow north",
        "debug shadow east",
        "debug footsteps 3",
        "look",
        "look",
    ])
    assert "A shadow flickers to the north." in out
    assert "A shadow flickers to the east." in out
    assert "You hear footsteps nearby." in out
    parts = out.split("On the ground lies:")
    assert len(parts) >= 3
    seg = parts[2]
    assert "A shadow flickers" not in seg
    assert "footsteps" not in seg


def test_invalid_footsteps_distance(cli_runner):
    enable_dev_env()
    out = cli_runner.run_commands(["debug footsteps 0"])
    assert "must be 1..4" in out or "Invalid" in out


def test_debug_clear(cli_runner):
    enable_dev_env()
    out = cli_runner.run_commands([
        "debug shadow south",
        "debug clear",
        "look",
    ])
    assert "A shadow flickers" not in out
