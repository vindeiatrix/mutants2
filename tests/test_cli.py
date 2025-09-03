import subprocess
import sys


def test_cli_smoke(tmp_path):
    cmd = [sys.executable, '-m', 'mutants2']
    # The game starts in the class menu; choose a class to begin play.
    inp = '1\nlook\nnorth\nlast\ntravel\nlook\nexit\n'
    result = subprocess.run(cmd, input=inp, text=True, capture_output=True, env={'HOME': str(tmp_path)})
    assert result.returncode == 0
    assert 'Compass:' in result.stdout


def _run_game(commands, tmp_path):
    cmd = [sys.executable, '-m', 'mutants2']
    inp = '1\n' + '\n'.join(commands) + '\n'
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
