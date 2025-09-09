from mutants2.testing_api import run_one


def test_travel_feedback():
    out = run_one("travel 2100")
    assert "ZAAAAPPPPP!! You've been sent to the year 2100 A.D." in out
    assert "Compass:" not in out
