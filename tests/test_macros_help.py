from mutants2.ui.help import MACROS_HELP


def test_help_macros_contains_key_sections(cli_runner):
    out = cli_runner.run_commands(["help macros"])
    assert "MACROS — define/run/edit" in out
    assert "macro add <name> = <script>" in out
    assert "Profiles (saved outside the savegame)" in out
    assert "Script language" in out
    assert "Speed-walk" in out
    assert "Safety & limits" in out
    assert "Examples" in out
