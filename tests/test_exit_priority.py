from mutants2.cli.shell import make_context


def test_exit_priority(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda *_: "1")
    ctx = make_context()
    assert ctx.dispatch_line("exit") is True
