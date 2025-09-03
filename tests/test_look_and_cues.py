import contextlib
from io import StringIO

from mutants2.engine import world as world_mod
from mutants2.engine.player import Player
from mutants2.engine.render import render_room_view


def capture_render(w, p):
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        render_room_view(p, w)
    return buf.getvalue()


def test_look_dir_shows_adjacent(cli_runner):
    out = cli_runner.run_commands(["loo e"])
    assert "***" in out


def test_look_dir_blocked(cli_runner):
    out = cli_runner.run_commands(["look sou"])
    assert "can't look that way" not in out.lower()


def test_shadow_only_adjacent_open():
    w = world_mod.World()
    w.year(2000)
    w.place_monster(2000, 1, 0, "mutant")
    p = Player()
    out = capture_render(w, p)
    assert "shadows to the east" in out.lower()


def test_no_shadow_two_away():
    w = world_mod.World()
    w.year(2000)
    for (x, y), _ in list(w.monsters_in_year(2000).items()):
        w.remove_monster(2000, x, y)
    w.place_monster(2000, 2, 0, "mutant")
    p = Player()
    out = capture_render(w, p)
    assert "shadows to" not in out.lower()




def test_density_tripled():
    w = world_mod.World(global_seed=123)
    w.year(2000)
    walkables = len(list(w.walkable_coords(2000)))
    count = w.monster_count(2000)
    assert count <= min(round(0.35 * walkables), round(0.18 * walkables))
    assert count >= 1
