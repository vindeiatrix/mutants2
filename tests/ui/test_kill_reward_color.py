import pytest
from mutants2.ui.theme import red
from mutants2.ui.render import render_kill_block


@pytest.mark.ui
def test_kill_reward_color(capsys):
    render_kill_block(2, 3)
    out = capsys.readouterr().out
    assert red("You collect 2 Riblets and 3 ions from the slain body.") in out
