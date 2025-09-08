import pytest
from mutants2.ui.theme import cyan, blue
from mutants2.ui.render import render_single_exit


@pytest.mark.ui
def test_exits_color_split():
    line = render_single_exit("north", "area continues.")
    assert line.startswith(cyan("north"))
    assert blue("area continues.") in line
