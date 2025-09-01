from mutants2.cli.keynames import normalize_key, keypad_fallback


def test_normalize_and_bind():
    assert normalize_key("kp4") == "kp4"
    assert keypad_fallback("kp4") == "4"
    assert normalize_key("F12") == "f12"
    assert normalize_key("x") == "x"
    assert normalize_key("bad") is None


def test_bindings_store_and_profile(cli_runner):
    out = cli_runner.run_commands([
        "macro bind kp4 = west",
        "macro bindings",
        "macro save testkeys",
        "macro clear",
        "yes",
        "macro load testkeys",
        "press 4",
    ])
    assert "kp4 = west" in out
    assert "> west" in out


def test_mudmaster_shim(cli_runner):
    out = cli_runner.run_commands([
        "/macro kp4 {west}",
        "press kp4",
    ])
    assert "> west" in out


def test_press_helper_executes(cli_runner):
    out = cli_runner.run_commands([
        "macro bind x = look",
        "press x",
    ])
    assert "> look" in out


def test_keys_toggle(cli_runner):
    out = cli_runner.run_commands([
        "macro bind x = look",
        "macro keys off",
        "press x",
        "macro keys on",
        "press x",
    ])
    assert out.count("> look") == 1


def test_safety_limits_respected(cli_runner):
    out = cli_runner.run_commands([
        "macro bind x = (look)*1001",
        "press x",
    ])
    assert "step limit" in out.lower()
