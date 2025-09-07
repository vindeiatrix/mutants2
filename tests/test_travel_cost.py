from __future__ import annotations

import contextlib
from io import StringIO

from mutants2.cli.shell import make_context
from mutants2.engine import persistence
from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.ui.theme import yellow


def run(
    commands: list[str],
    *,
    ions: int = 0,
    start_year: int = 2000,
    start_pos: tuple[int, int] = (0, 0),
):
    w = World()
    w.year(start_year)
    p = Player(year=start_year, ions=ions)
    p.positions[start_year] = start_pos
    save = persistence.Save()
    ctx = make_context(p, w, save)
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        for cmd in commands:
            ctx.dispatch_line(cmd)
    return buf.getvalue(), p


def test_travel_cost_deducts_per_century():
    out, p = run(["travel 2500"], ions=20_000)
    assert yellow("ZAAAAPPPPP!! You've been sent to the year 2500 A.D.") in out
    # 5 century steps -> 15,000 ion cost
    assert p.year == 2500 and p.ions == 5_000


def test_travel_costs_when_travelling_backward():
    out, p = run(["travel 2300"], ions=20_000, start_year=2800)
    assert yellow("ZAAAAPPPPP!! You've been sent to the year 2300 A.D.") in out
    assert p.year == 2300 and p.ions == 5_000


def test_travel_insufficient_ions_no_move():
    out, p = run(["travel 2500"], ions=14_000)
    assert yellow("***") in out
    assert yellow("You don't have enough ions to create a portal.") in out
    assert p.year == 2000 and p.ions == 14_000


def test_same_century_travel_free_and_resets_position():
    out, p = run(["east", "travel 2700"], ions=5_000, start_year=2700, start_pos=(1, 0))
    assert yellow("You're already in the 27th Century!") in out
    assert p.ions == 5_000
    assert p.positions[2700] == (0, 0)
