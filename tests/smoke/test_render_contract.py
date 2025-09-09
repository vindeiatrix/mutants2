from mutants2.testing_api import run_one


def test_render_contract():
    out = run_one("look")
    lines = out.strip().splitlines()
    assert lines[0] == "look"
    assert "Compass:" in out
    assert "***" in out
