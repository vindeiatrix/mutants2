import os
import sys
from pathlib import Path

import pytest

# Ensure the package root is importable when tests run from within the tests directory
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def cli_runner(tmp_path):
    import subprocess

    class Runner:
        def run_commands(self, commands):
            cmd = [sys.executable, "-m", "mutants2"]
            env = os.environ.copy()
            env.setdefault("HOME", str(tmp_path))
            inp = "1\n" + "\n".join(commands + ["exit"]) + "\n"
            result = subprocess.run(cmd, input=inp, text=True, capture_output=True, env=env)
            return result.stdout

    return Runner()
