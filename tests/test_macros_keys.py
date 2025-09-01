def test_bind_kp4_char_fallback(cli_runner):
    out = cli_runner.run_commands([
        "macro bind kp4 = west",
        "press 4",
    ])
    assert "> west" in out


def test_bind_char(cli_runner):
    out = cli_runner.run_commands([
        "macro bind z = look",
        "press z",
    ])
    assert "> look" in out


def test_mudmaster_shorthand(cli_runner):
    out = cli_runner.run_commands([
        "/macro kp5 {look}",
        "press 5",
    ])
    assert "> look" in out


def test_keys_toggle(cli_runner):
    out = cli_runner.run_commands([
        "macro bind z = look",
        "macro keys off",
        "press z",
        "macro keys on",
        "press z",
    ])
    assert out.count("> look") == 1


def test_limits(cli_runner):
    out = cli_runner.run_commands([
        "macro bind x = (look)*1001",
        "press x",
    ])
    assert "step limit" in out.lower()

