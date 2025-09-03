import contextlib
from io import StringIO

from mutants2.engine.world import World, GRID_MIN
from mutants2.engine.player import Player
from mutants2.render import render_current_room
from mutants2.data.room_headers import ROOM_HEADERS
from mutants2.ui.theme import red


def capture_room(w, p):
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        print(render_current_room(p, w))
    return buf.getvalue().splitlines()


def test_headers_deterministic():
    w = World(global_seed=123)
    p = Player()
    h1 = w.room_description(p.year, p.x, p.y)
    h2 = w.room_description(p.year, p.x, p.y)
    assert h1 == h2
    h3 = w.room_description(p.year, p.x + 1, p.y)
    assert h1 in ROOM_HEADERS and h3 in ROOM_HEADERS
    lines = capture_room(w, p)
    assert lines[0] == red(h1)


def test_struck_back_boundary():
    w = World()
    p = Player()
    p.positions[p.year] = (GRID_MIN, 0)
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        moved = p.move("west", w)
        print(render_current_room(p, w))
    out = buf.getvalue().splitlines()
    assert moved is False
    assert p._last_move_struck_back
    assert "struck back" in out[0].lower()
    assert (p.x, p.y) == (GRID_MIN, 0)
    assert out[1] in {red(h) for h in ROOM_HEADERS}
