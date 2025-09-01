import subprocess
import sys


def test_cli_smoke(tmp_path):
    cmd = [sys.executable, '-m', 'mutants2']
    # The game starts in the class menu; choose a class to begin play.
    inp = '1\nlook\nnorth\nlast\ntravel\nlook\nexit\n'
    result = subprocess.run(cmd, input=inp, text=True, capture_output=True, env={'HOME': str(tmp_path)})
    assert result.returncode == 0
    assert 'On the ground lies' in result.stdout
