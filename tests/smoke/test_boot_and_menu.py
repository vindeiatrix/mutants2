from mutants2.testing_api import run_one


def test_boot_and_menu():
    out = run_one("menu")
    assert out.splitlines()[0] == "menu"
    assert "You're menuing!" in out
