import subprocess
import sys

from mutants2.engine import persistence


def run_cli(inp, home):
    cmd = [sys.executable, '-m', 'mutants2']
    return subprocess.run(cmd, input=inp, text=True, capture_output=True, env={'HOME': str(home)})


def test_default_class(tmp_path, monkeypatch):
    monkeypatch.setenv('HOME', str(tmp_path))
    player = persistence.load()
    assert player.clazz == 'Warrior'
    player2 = persistence.load()
    assert player2.clazz == 'Warrior'


def test_select_and_switch_class(tmp_path):
    home = tmp_path
    # First run: should default to Warrior
    result = run_cli('back\nlook\nexit\n', home)
    assert 'Class: Warrior' in result.stdout
    # Choose Mage
    run_cli('2\nback\nexit\n', home)
    # Verify persisted Mage
    result = run_cli('back\nlook\nexit\n', home)
    assert 'Class: Mage' in result.stdout
    # Switch to Thief
    run_cli('4\nback\nexit\n', home)
    # Verify persisted Thief
    result = run_cli('back\nlook\nexit\n', home)
    assert 'Class: Thief' in result.stdout
