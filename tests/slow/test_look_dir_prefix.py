import pytest

import contextlib
from io import StringIO


from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.cli import shell
from mutants2.ui.theme import yellow


@pytest.fixture
def world_open_north():
    return None


@pytest.fixture
def world_blocked_south():
    return None


@pytest.fixture
def cli_with_monster(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    w = world_mod.World()
    w.year(2000)
    w.place_monster(2000, 0, 0, "night_stalker")
    p = Player()
    save = persistence.Save()
    ctx = shell.make_context(p, w, save)

    class CLI:
        def run(self, commands):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                for cmd in commands:
                    ctx.dispatch_line(cmd)
            return buf.getvalue()

    return CLI()


def test_look_dir_accepts_prefix(cli_runner, world_open_north):
    assert "***" in cli_runner.run_commands(["look n"])
    assert "***" in cli_runner.run_commands(["loo no"])
    assert "***" in cli_runner.run_commands(["look nor"])
    assert "***" in cli_runner.run_commands(["look north"])


def test_look_blocked_with_prefix(cli_runner):
    out = cli_runner.run_commands(["look so"])
    assert "can't look that way" not in out.lower()


def test_movement_rules_unchanged(cli_runner):
    assert "***" in cli_runner.run_commands(["n"])
    assert "***" in cli_runner.run_commands(["north"])
    assert yellow("You're noing!") in cli_runner.run_commands(["no"])


def test_look_precedence_monster_over_dir(cli_with_monster):
    out = cli_with_monster.run(["loo n"])
    assert "night-stalker" in out.lower()
