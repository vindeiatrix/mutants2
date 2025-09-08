from mutants2.testing_api import run_one


def test_look_smoke():
    out = run_one("look")
    lines = out.strip().splitlines()
    assert lines[0] == "look"
    assert lines.count("look") == 1
    assert "Compass:" in out
    assert "***" in out


def test_travel_smoke():
    out = run_one("travel 2100")
    lines = out.strip().splitlines()
    assert lines[0] == "travel 2100"
    assert lines.count("travel 2100") == 1
    assert "Compass:" in out
    assert "footsteps" not in out.lower()
