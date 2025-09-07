import subprocess
import sys


def run_cli(inp, home, env_extra=None):
    cmd = [sys.executable, "-m", "mutants2"]
    env = {"HOME": str(home)}
    if env_extra:
        env.update(env_extra)
    return subprocess.run(cmd, input=inp, text=True, capture_output=True, env=env)


def test_class_selection_digits_enters_game(tmp_path):
    result = run_cli("1\nexit\n", tmp_path)
    out = result.stdout
    assert "Compass:" in out
    assert "***" in out


def test_class_selection_names_enters_game(tmp_path):
    result = run_cli("wizard\nexit\n", tmp_path)
    out = result.stdout
    assert "Compass:" in out
    assert "***" in out


def test_invalid_then_valid(tmp_path):
    result = run_cli("xyz\n2\nexit\n", tmp_path)
    out = result.stdout
    assert "Invalid selection." in out
    assert "Compass:" in out


def test_back_behavior(tmp_path):
    inp = "back\n1\nclass\nback\nlook\nexit\n"
    result = run_cli(inp, tmp_path)
    out = result.stdout
    assert "Pick a class to begin." in out
    assert out.count("Compass:") >= 2


def test_persistence_of_class(tmp_path):
    home = tmp_path
    run_cli("1\nnorth\nexit\n", home)
    result = run_cli("sta\nexit\n", home)
    out = result.stdout
    assert "Mutant Thief" in out
    assert "Choose your class" not in out


def test_debug_unavailable_in_menu(tmp_path):
    home = tmp_path
    env = {"MUTANTS2_DEV": "1"}
    result = run_cli("debug shadow north\n1\ndebug shadow north\nexit\n", home, env)
    out = result.stdout
    assert "Debug commands are available only in dev mode (in-game)." in out
    assert "OK." in out  # debug works in-game


def test_exit_from_class_menu(tmp_path):
    result = run_cli("exit\n", tmp_path)
    out = result.stdout
    assert "Goodbye." in out
    assert "Compass:" not in out


def test_question_in_class_menu_shows_help(tmp_path):
    result = run_cli("?\nexit\n", tmp_path)
    out = result.stdout
    assert "Commands:" in out
    assert "Compass:" not in out
