import datetime

from mutants2.engine.world import World
from mutants2.engine.player import Player
from mutants2.engine import persistence
from mutants2.engine.gen import daily_topup_if_needed, daily_topup_year


def make_game():
    w = World()
    p = Player()
    w.year(p.year)  # ensure generation and initial seeding
    save = persistence.Save()
    return w, p, save


def test_topup_runs_once_per_day():
    w, p, save = make_game()
    save.fake_today_override = "2025-09-01"
    first = daily_topup_if_needed(w, p, save)
    second = daily_topup_if_needed(w, p, save)
    assert first >= 0
    assert second == 0


def test_topup_advances_next_day():
    w, p, save = make_game()
    save.fake_today_override = "2025-09-01"
    daily_topup_if_needed(w, p, save)
    # remove some items
    removed = 0
    for key in list(w.ground.keys()):
        yr, _, _ = key
        if yr == p.year and removed < 5:
            del w.ground[key]
            removed += 1
    save.fake_today_override = "2025-09-02"
    n = daily_topup_if_needed(w, p, save)
    assert n > 0


def test_topup_never_exceeds_target():
    w, p, save = make_game()
    today = datetime.date(2025, 9, 2)
    placed = daily_topup_year(w, p.year, save.global_seed, today)
    assert placed == 0


def test_topup_deterministic_same_day():
    w, p, save = make_game()
    # remove existing items to force placements
    w.ground = {k: v for k, v in w.ground.items() if k[0] != p.year}
    base_ground = w.ground.copy()
    w1 = World(base_ground.copy(), set(w.seeded_years))
    w2 = World(base_ground.copy(), set(w.seeded_years))
    today = datetime.date(2025, 9, 3)
    daily_topup_year(w1, p.year, save.global_seed, today)
    daily_topup_year(w2, p.year, save.global_seed, today)
    assert w1.ground == w2.ground

