import pytest
from mutants2.ui.theme import red
from mutants2.ui.render import render_kill_block


@pytest.mark.ui
def test_kill_reward_color(capsys):
    render_kill_block("Mutant-1", 1, 2, 3)
    out = capsys.readouterr().out
    assert red("You have slain Mutant-1!") in out
    assert red("Your experience points are increased by 1!") in out
    assert red("You collect 2 Riblets and 3 ions from the slain body.") in out
