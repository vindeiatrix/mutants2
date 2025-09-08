import contextlib
from io import StringIO


from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world as world_mod
from mutants2.engine.player import Player
from mutants2.engine.ai import set_aggro


def run_cli(world, commands, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    save = persistence.Save()
    p = Player(ions=100000)
    p.clazz = "Warrior"
    ctx = make_context(p, world, save)
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        for cmd in commands:
            ctx.dispatch_line(cmd)
    return buf.getvalue()


def test_yell_once_on_aggro(tmp_path, monkeypatch):
    w = world_mod.World()
    w.year(2000)
    for (x, y), _ in list(w.monsters_in_year(2000).items()):
        w.remove_monster(2000, x, y)
    w.place_monster(2000, 0, 0, "mutant")

    def always(year, x, y, player, seed_parts=()):
        yells = []
        for m in w.monsters_here(year, x, y):
            msg = set_aggro(m)
            if msg:
                yells.append(msg)
        return yells

    monkeypatch.setattr(w, "on_entry_aggro_check", always)
    out = run_cli(w, ["look", "look"], tmp_path, monkeypatch)
    assert out.count("yells at you!") == 1


def test_same_century_travel_teleports(tmp_path, monkeypatch):
    w = world_mod.World()
    for yr in (2000, 2100):
        w.year(yr)
        for (x, y), _ in list(w.monsters_in_year(yr).items()):
            w.remove_monster(yr, x, y)
    out = run_cli(
        w, ["travel 2100", "east", "travel 2100", "look"], tmp_path, monkeypatch
    )
    lines = out.splitlines()
    idxs = [i for i, ln in enumerate(lines) if ln == "travel 2100"]
    second = idxs[1]
    assert "You're already in the 21st Century!" in lines[second + 1]
    look_idx = lines.index("look", second + 1)
    assert any("Compass" in ln for ln in lines[second + 1 : look_idx])
    assert any("Compass: (0E : 0N)" in ln for ln in lines[look_idx + 1 :])


def test_travel_triggers_arrival(tmp_path, monkeypatch):
    w = world_mod.World()
    w.year(2000)
    for (x, y), _ in list(w.monsters_in_year(2000).items()):
        w.remove_monster(2000, x, y)
    w.place_monster(2000, 1, 0, "mutant")
    w.monster_here(2000, 1, 0)["aggro"] = True
    out = run_cli(w, ["travel 2000"], tmp_path, monkeypatch)
    assert "You're already in the 20th Century!" in out
    assert "has just arrived from the east" in out
    assert "Compass" not in out
