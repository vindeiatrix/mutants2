def test_char_binding_via_line_fallback(cli_runner):
    out = cli_runner.run_commands([
        "macro bind z = look",
        "z",
    ])
    assert "***" in out and "Class:" in out


def test_kp_binding_triggers_with_digit(cli_runner):
    out = cli_runner.run_commands([
        "macro bind kp4 = west",
        "4",
        "look",
    ])
    assert "Unknown command" not in out


def test_builtin_precedence(cli_runner):
    out = cli_runner.run_commands([
        "macro bind n = look",
        "n",
    ])
    assert "Unknown command" not in out


def test_keys_off_disables_fallback(cli_runner):
    out = cli_runner.run_commands([
        "macro bind z = look",
        "macro keys off",
        "z",
    ])
    assert "Unknown command" in out
