try:  # prompt_toolkit is optional
    from prompt_toolkit import PromptSession
    from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
except Exception:  # pragma: no cover - graceful fallback when ptk missing
    PromptSession = KeyBindings = merge_key_bindings = None

from mutants2.cli.keynames import KEYPAD
from mutants2.engine.macros import resolve_bound_script


def _fallback_char_for(key: str) -> str | None:
    """Return printable char for a key or keypad alias."""
    if key in KEYPAD:
        return KEYPAD[key][1]
    return key if len(key) == 1 and key.isprintable() else None


def _keys_enabled(store) -> bool:
    return getattr(store, "keys_enabled", True)


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

    def _run_script_now(self, app, script: str) -> None:
        """Suspend the prompt, run the script, then refresh the prompt UI."""

        def _fn():
            self.ctx.run_script(script)
            import sys
            try:
                sys.stdout.flush()
            except Exception:
                pass

        app.run_in_terminal(_fn, in_executor=False)
        app.invalidate()

    def _install_core_bindings(self) -> None:
        kb = self.core_bindings

        @kb.add("enter")
        def _(event) -> None:
            event.app.current_buffer.validate_and_handle()

    def _rebuild_dynamic_bindings(self) -> None:
        store = self.ctx.macro_store
        kb = KeyBindings()

        chars: set[str] = set()
        for key in store.bindings().keys():
            ch = _fallback_char_for(key)
            if ch:
                chars.add(ch)

        for ch in chars:
            @kb.add(ch, eager=True)
            def _(event, _ch=ch):
                app = event.app
                if app.current_buffer.text or not _keys_enabled(store):
                    return
                script = resolve_bound_script(store, _ch)
                if getattr(store, "keys_debug", False):
                    print(f"[#] key='{_ch}' -> {'hit' if bool(script) else 'miss'}")
                if script:
                    app.current_buffer.reset()
                    self._run_script_now(app, script)
                else:
                    app.current_buffer.insert_text(_ch)

        self.dynamic_bindings = kb

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
