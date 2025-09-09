import pytest
from mutants2.ui.theme import COLOR_HEADER, COLOR_ITEM
from mutants2.ui.render import render_single_exit


@pytest.mark.ui
def test_exits_color_split():
    line = render_single_exit("north", "area continues.")
    assert line.startswith(COLOR_HEADER("north"))
    assert COLOR_ITEM("area continues.") in line
