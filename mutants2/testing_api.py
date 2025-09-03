"""Helpers for deterministic, single-command CLI tests."""

from __future__ import annotations

import contextlib
import io
import re
import tempfile
from pathlib import Path

from .cli.shell import make_context
from .engine import world as world_mod, persistence
from .engine.player import Player


def run_one(cmd: str, *, seed: int = 42, year: int | None = None) -> str:
    """Execute ``cmd`` and return the game's printed output.

    The world is bootstrapped deterministically using ``seed``.  Only one
    command is executed and its output captured.  ``year`` selects the starting
    year (default 2000).
    """

    start_year = 2000 if year is None else year
    save = persistence.Save(global_seed=seed)
    w = world_mod.World(global_seed=seed)
    w.year(start_year)
    p = Player(year=start_year, clazz="Warrior")
    ctx = make_context(p, w, save)

    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            ctx.dispatch_line(cmd)
    output = buf.getvalue()
    buf.close()
    # Strip ANSI color codes just in case
    output = re.sub(r"\x1b\[[0-9;]*m", "", output)
    return output
