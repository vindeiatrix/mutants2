from mutants2.cli.keynames import normalize_key, keypad_fallback
import pytest


def test_normalize_and_bind():
    assert normalize_key("kp4") == "kp4"
    assert keypad_fallback("kp4") == "4"
    assert normalize_key("F12") == "f12"
    assert normalize_key("x") == "x"
    assert normalize_key("bad") is None


def test_bind_kp4_falls_back_to_char(cli_runner):
    out = cli_runner.run_commands([
        "macro bind kp4 = west",
        "press 4",
    ])
    assert "> west" in out


def test_bind_char_works(cli_runner):
    out = cli_runner.run_commands([
        "macro bind 5 = look",
        "press 5",
    ])
    assert "> look" in out


def test_keys_enabled_toggle(cli_runner):
    out = cli_runner.run_commands([
        "macro bind 4 = look",
        "macro keys off",
        "press 4",
        "macro keys on",
        "press 4",
    ])
    assert out.count("> look") == 1


def test_mudmaster_shorthand(cli_runner):
    out = cli_runner.run_commands([
        "/macro kp5 {look}",
        "press 5",
    ])
    assert "> look" in out


@pytest.mark.skip("Prompt-toolkit handler only; helper bypasses buffer")
def test_line_not_empty_no_intercept():
    pass


def test_safety_limits_respected(cli_runner):
    out = cli_runner.run_commands([
        "macro bind x = (look)*1001",
        "press x",
    ])
    assert "step limit" in out.lower()

