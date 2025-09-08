import os
import datetime


from mutants2.engine import persistence, items
from mutants2.engine.player import Player
from mutants2.engine.world import World
from mutants2.ui.theme import yellow


def test_monster_bait_conversion(cli_runner, tmp_path):
    persistence.SAVE_PATH = tmp_path / ".mutants2" / "save.json"
    os.environ["HOME"] = str(tmp_path)
    p = Player()
    p.inventory.append("monster_bait")
    w = World(seeded_years={2000})
    save = persistence.Save()
    save.last_topup_date = datetime.date.today().isoformat()
    persistence.save(p, w, save)
    out = cli_runner.run_commands(["convert MONSTER_BAIT", "inventory", "status"])
    item = items.REGISTRY["monster_bait"]
    assert item.weight_lbs == 10
    assert item.ion_value == 10000
    assert yellow("The Monster-Bait vanishes with a flash!") in out
    assert yellow("You convert the Monster-Bait into 10000 ions.") in out
    assert "(empty)" not in out
    assert "Ions         : 40000" in out


def test_convert_gibberish(cli_runner):
    out = cli_runner.run_commands(["con asd"])
    assert yellow("***") in out
    assert yellow("You're not carrying a asd.") in out


def test_travel_rounding_and_stats(cli_runner):
    out = cli_runner.run_commands(["tra 2345", "status"])
    assert yellow("ZAAAAPPPPP!! You've been sent to the year 2300 A.D.") in out
    assert "Year A.D.     : 2300" in out


def test_travel_out_of_range(cli_runner):
    out = cli_runner.run_commands(["travel 23452353"])
    assert yellow("You can only travel from year 2000 to 3000!") in out


def test_command_usage_blocks(cli_runner):
    out = cli_runner.run_commands(["tra"])
    assert "TRAVEL [year]" in out
    out2 = cli_runner.run_commands(["con"])
    assert "Type CONVERT [item name] to convert an item." in out2


def test_ground_item_density():
    w = World()
    w.year(2000)
    cnt = w.ground_items_count(2000)
    assert 360 <= cnt <= 440
