try:  # prompt_toolkit is optional
    from prompt_toolkit import PromptSession
    from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
    from prompt_toolkit.filters import Condition
except Exception:  # pragma: no cover - graceful fallback when ptk missing
    PromptSession = KeyBindings = merge_key_bindings = Condition = None

from mutants2.cli.keynames import KEYPAD
from mutants2.engine.macros import resolve_bound_script


def _fallback_char_for(key: str) -> str | None:
    if key in KEYPAD:
        return KEYPAD[key][1]
    return key if len(key) == 1 else None


class FallbackRepl:
    def __init__(self, context) -> None:
        self.ctx = context

    def run(self) -> None:
        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                print("")
                break
            if self.ctx.dispatch_line(line):
                break


class PtkRepl:
    def __init__(self, ctx):
        self.ctx = ctx
        self.session: PromptSession | None = None
        self.core_bindings = KeyBindings()
        self.dynamic_bindings = KeyBindings()
        self.dynamic_chars: set[str] = set()

    def _install_core_bindings(self) -> None:
        kb = self.core_bindings

        @kb.add("enter")
        def _(event) -> None:
            event.app.current_buffer.validate_and_handle()

    def _rebuild_dynamic_bindings(self) -> None:
        kb = KeyBindings()
        store = self.ctx.macro_store
        buffer_empty = Condition(lambda: event_app().current_buffer.text == "")
        keys_enabled = Condition(lambda: getattr(store, "keys_enabled", True))

        def event_app():
            from prompt_toolkit.application.current import get_app
            return get_app()

        chars: set[str] = set()
        for key, script in store.bindings().items():
            ch = _fallback_char_for(key)
            if not ch:
                continue
            if len(ch) == 1 and ch.isprintable():
                chars.add(ch)

        for ch in chars:
            @kb.add(ch, filter=buffer_empty & keys_enabled)
            def _(event, _ch=ch):
                script = resolve_bound_script(store, _ch)
                if script:
                    event.app.current_buffer.reset()
                    self.ctx.run_script(script)

        self.dynamic_bindings = kb
        self.dynamic_chars = chars

    def _make_session(self) -> None:
        bindings = merge_key_bindings([self.core_bindings, self.dynamic_bindings])
        self.session = PromptSession(key_bindings=bindings, enable_history_search=True)

    def _refresh_session_keymap(self) -> None:
        assert self.session is not None
        self.session.app.key_bindings = merge_key_bindings(
            [self.core_bindings, self.dynamic_bindings]
        )

    def run(self) -> None:
        self._install_core_bindings()
        self._rebuild_dynamic_bindings()
        self._make_session()

        self.ctx.macro_store._on_bindings_changed = self._on_bindings_changed

        while True:
            try:
                line = self.session.prompt("> ")
            except (EOFError, KeyboardInterrupt):
                print("")
                break
            if self.ctx.dispatch_line(line):
                break

    def _on_bindings_changed(self) -> None:
        self._rebuild_dynamic_bindings()
        self._refresh_session_keymap()
