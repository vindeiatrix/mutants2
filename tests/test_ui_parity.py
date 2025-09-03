import re

from mutants2.render import render_room_at
from mutants2.engine.world import World
from mutants2.engine.player import Player

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def test_empty_ground_no_section():
    w = World(seeded_years={2000})
    w.year(2000)
    out = strip_ansi(render_room_at(w, 2000, 0, 0))
    assert "On the ground" not in out


def test_single_item_and_stack():
    w = World({(2000, 0, 0): ["nuclear_thong", "nuclear_thong"]}, {2000})
    out = strip_ansi(render_room_at(w, 2000, 0, 0))
    assert "On the ground lies:" in out
    assert "A Nuclear-Thong, A Nuclear-Thong (1)." in out


def test_render_order_and_copy():
    w = World({(2000, 0, 0): "ion_decay"}, {2000})
    w.place_monster(2000, 0, 0, "mutant")
    w.place_monster(2000, 1, 0, "mutant")
    out = strip_ansi(render_room_at(w, 2000, 0, 0))
    lines = out.splitlines()
    # description then compass
    assert lines[1].startswith("Compass: (")
    # exits contain copy
    exit_lines = [ln for ln in lines[2:] if "area continues." in ln]
    assert exit_lines and exit_lines[0].endswith("area continues.")
    # separators and sections order
    idxs = [i for i, ln in enumerate(lines) if ln == "***"]
    assert idxs and lines[idxs[0] - 2] == "On the ground lies:"
    assert "You see shadows to the" in lines[idxs[0] + 1]
    assert "Mutant is here." in lines[-1]
    assert "Class:" not in out
