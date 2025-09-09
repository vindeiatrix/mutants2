from mutants2.testing_api import run_one


def test_compass_and_exits_colors():
    out = run_one("look")
    assert "Compass: (0E : 0N)" in out
    assert "north – area continues." in out
    assert "south – area continues." in out
