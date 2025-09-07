def test_add_run_basic(cli_runner):
    out = cli_runner.run_commands(
        [
            "macro add scout = look; n*2; look",
            "@scout",
        ]
    )
    assert out.count("> look") >= 2
    assert "> n" in out


def test_parameters_and_do(cli_runner):
    out = cli_runner.run_commands(
        [
            "macro add getn = get $*; north; look",
            "macro run getn Ion-Decay",
            "do (east; look)*2",
        ]
    )
    assert "> get Ion-Decay" in out
    assert out.count("> east") >= 2


def test_speedwalk(cli_runner):
    out = cli_runner.run_commands(
        [
            "do 3n2e",
        ]
    )
    assert out.count("> n") == 3
    assert out.count("> e") == 2


def test_repeat_limits(cli_runner):
    out = cli_runner.run_commands(["do (look)*1001"])
    assert "step limit" in out.lower()


def test_profiles_save_load(cli_runner):
    out = cli_runner.run_commands(
        [
            "macro add a = look",
            "macro save test1",
            "macro clear",
            "yes",
            "macro load test1",
            "@a",
            "macro profiles",
        ]
    )
    assert "> look" in out
    assert "test1" in out


def test_echo_toggle(cli_runner):
    out = cli_runner.run_commands(
        [
            "macro add a = look",
            "@a",
            "macro echo off",
            "@a",
            "macro echo on",
            "@a",
        ]
    )
    assert out.count("> look") == 2


def test_wait_caps(cli_runner):
    out = cli_runner.run_commands(["do wait 5000; look"])
    assert "> wait 5000" in out
    assert "> look" in out
