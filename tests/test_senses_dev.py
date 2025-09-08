import os


def enable_dev_env():
    os.environ["MUTANTS2_DEV"] = "1"


def test_debug_commands_rejected_without_dev(cli_runner):
    os.environ.pop("MUTANTS2_DEV", None)
    out = cli_runner.run_commands(["debug shadow north", "look"])
    assert "Debug commands are available only in dev mode." in out


def test_shadow_render_once(cli_runner):
    enable_dev_env()
    out = cli_runner.run_commands(
        [
            "debug clear",
            "debug shadow north",
            "debug shadow east",
            "look",
            "look",
        ]
    )
    assert out.count("You see shadows") == 1


def test_debug_clear(cli_runner):
    enable_dev_env()
    out = cli_runner.run_commands(
        [
            "debug shadow south",
            "debug clear",
            "look",
        ]
    )
    assert "You see shadows to the south" not in out
