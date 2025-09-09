from mutants2.cli.shell import make_context
from mutants2.engine import persistence, world


def test_exit_priority(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda *_: "1")
    p, ground, monsters, seeded, save = persistence.load()
    w = world.World(ground, seeded, monsters, global_seed=save.global_seed)
    p.clazz = "Warrior"
    ctx = make_context(p, w, save)
    assert ctx.dispatch_line("exit") is True
