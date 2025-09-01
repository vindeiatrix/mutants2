from mutants2.engine.macros import resolve_bound_script


class FallbackRepl:
    def __init__(self, context) -> None:
        self.ctx = context
        self.ctx.macro_store.repl_mode = "Fallback"

    def run(self) -> None:
        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                print("")
                break
            self.ctx.dispatch_line(line)


class PtkRepl:
    def __init__(self, context) -> None:
        self.ctx = context
        from prompt_toolkit import PromptSession
        from prompt_toolkit.key_binding import KeyBindings

        self.PromptSession = PromptSession
        self.KeyBindings = KeyBindings
        self.ctx.macro_store.repl_mode = "PTK"

    def run(self) -> None:
        kb = self.KeyBindings()
        session = self.PromptSession(key_bindings=kb, enable_history_search=True)
        store = self.ctx.macro_store

        def debug(msg: str) -> None:
            if getattr(store, "keys_debug", False):
                print(msg)

        def try_fire(event, key_id: str | None, ch: str | None) -> bool:
            buf = event.app.current_buffer
            if not store.keys_enabled or buf.text:
                return False
            key_display = key_id or ch or "?"
            script = resolve_bound_script(store, key_id) if key_id else None
            if not script and ch:
                script = resolve_bound_script(store, ch)
            debug(f"[#] key='{key_display}' data='{ch or ''}' → resolved={'yes' if script else 'no'}")
            if not script:
                return False
            event.prevent_default()
            buf.reset()
            self.ctx.run_script(script)
            return True

        @kb.add("<any>")
        def _(event):
            ch = event.data
            if ch and try_fire(event, None, ch):
                return
            # otherwise let PTK handle normally

        names = [
            "up",
            "down",
            "left",
            "right",
            "home",
            "end",
            "pageup",
            "pagedown",
            "tab",
            "escape",
            "space",
        ] + [f"f{i}" for i in range(1, 13)]

        for name in names:
            try:
                @kb.add(name)
                def _(event, _n=name):
                    try_fire(event, _n, None)
            except Exception:
                pass

        while True:
            try:
                line = session.prompt("> ")
            except (EOFError, KeyboardInterrupt):
                print("")
                break
            self.ctx.dispatch_line(line)
