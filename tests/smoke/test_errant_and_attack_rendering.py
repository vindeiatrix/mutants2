from mutants2.cli.shell import make_context
from mutants2.engine import world as world_mod, persistence
from mutants2.engine.player import Player

import io, contextlib, tempfile, re
from pathlib import Path

def run_commands(cmds, *, seed=42, setup=None):
    save = persistence.Save(global_seed=seed)
    w = world_mod.World(global_seed=seed)
    w.year(2000)
    p = Player(year=2000, clazz="Warrior")
    if setup:
        setup(w, p)
    ctx = make_context(p, w, save)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        persistence.SAVE_PATH = Path(tmp) / "save.json"
        with contextlib.redirect_stdout(buf):
            for c in cmds:
                ctx.dispatch_line(c)
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    buf.close()
    return out, w, p, ctx


def test_attack_no_room_block_but_arrival():
    def setup(w, p):
        w.place_monster(2000, 0, 0, "mutant")
        w.monster_here(2000, 0, 0)["hp"] = 2
        w.place_monster(2000, 1, 0, "mutant")
        w.monster_here(2000, 1, 0)["aggro"] = True
    out, w, _p, _ = run_commands(["attack"], setup=setup)
    assert "You are here." not in out
    assert "Compass:" not in out
    assert "You defeat the Mutant." in out
    assert "has just arrived from the west." in out


def test_single_token_gibberish():
    cases = {
        "pluck": "plucking",
        "love": "loving",
        "what": "whatting",
        "plow": "plowing",
        "34": "34ing",
    }
    for src, ger in cases.items():
        out, w, _p, _ = run_commands([src])
        lines = out.strip().splitlines()
        assert lines == [src, "***", f"You're {ger}!"]
        assert w.turn == 0


def test_gibberish_with_spaces():
    phrases = ["pow one", "i am smart"]
    for cmd in phrases:
        out, w, _p, _ = run_commands([cmd])
        lines = out.strip().splitlines()
        assert lines == [cmd, "***", "Type ? if you need assistance."]
        assert w.turn == 0
