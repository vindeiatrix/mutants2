from types import SimpleNamespace

from mutants2.cli.repl import PtkRepl
from mutants2.engine.macros import MacroStore


class DummyBuffer:
    def __init__(self, text: str = "") -> None:
        self.text = text

    def reset(self) -> None:
        self.text = ""

    def insert_text(self, text: str) -> None:
        self.text += text


class DummyApp:
    def __init__(self, buffer: DummyBuffer) -> None:
        self.current_buffer = buffer

    def run_in_terminal(self, fn, in_executor: bool = False) -> None:  # pragma: no cover - trivial
        fn()

    def invalidate(self) -> None:  # pragma: no cover - trivial
        pass


def _make_repl(run_log):
    store = MacroStore()
    ctx = SimpleNamespace(macro_store=store, run_script=lambda s: run_log.append(s))
    repl = PtkRepl(ctx)
    return repl, store


def _binding_for(repl: PtkRepl, key: str):
    [binding] = [b for b in repl.dynamic_bindings.bindings if b.keys == (key,)]
    return binding


def test_bound_char_runs_macro():
    run_log = []
    repl, store = _make_repl(run_log)
    store.bind("z", "look")
    repl._rebuild_dynamic_bindings()
    binding = _binding_for(repl, "z")

    buf = DummyBuffer()
    app = DummyApp(buf)
    event = SimpleNamespace(app=app)

    binding.handler(event)

    assert run_log == ["look"]
    assert buf.text == ""
    assert binding.eager()


def test_bound_char_ignored_when_buffer_not_empty():
    run_log = []
    repl, store = _make_repl(run_log)
    store.bind("z", "look")
    repl._rebuild_dynamic_bindings()
    binding = _binding_for(repl, "z")

    buf = DummyBuffer("x")
    app = DummyApp(buf)
    event = SimpleNamespace(app=app)

    binding.handler(event)

    assert run_log == []
    assert buf.text == "x"


def test_unbound_char_not_registered():
    run_log = []
    repl, store = _make_repl(run_log)
    store.bind("z", "look")
    repl._rebuild_dynamic_bindings()

    assert repl.dynamic_bindings.get_bindings_for_keys(("x",)) == []

