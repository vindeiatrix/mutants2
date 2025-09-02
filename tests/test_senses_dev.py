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
            inp = "1\n" + "\n".join(commands + ["exit"]) + "\n"
            result = subprocess.run(cmd, input=inp, text=True, capture_output=True, env=env)
            return result.stdout

    return Runner()


def test_debug_commands_rejected_without_dev(cli_runner):
    os.environ.pop("MUTANTS2_DEV", None)
    out = cli_runner.run_commands(["debug shadow north", "look"])
    assert "Debug commands are available only in dev mode." in out


def test_shadow_render_once(cli_runner):
    enable_dev_env()
    out = cli_runner.run_commands([
        "debug clear",
        "debug shadow north",
        "debug shadow east",
        "look",
        "look",
    ])
    assert "You see shadows to the east, north." in out
    parts = out.split("On the ground lies:")
    assert len(parts) >= 3
    seg = parts[-1]
    assert "You see shadows" not in seg


def test_debug_clear(cli_runner):
    enable_dev_env()
    out = cli_runner.run_commands([
        "debug shadow south",
        "debug clear",
        "look",
    ])
    assert "You see shadows to the south" not in out
