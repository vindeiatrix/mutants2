from mutants2.engine.macros import resolve_bound_script


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
    def __init__(self, context) -> None:
        self.ctx = context
        from prompt_toolkit import PromptSession
        from prompt_toolkit.key_binding import KeyBindings

        self.PromptSession = PromptSession
        self.KeyBindings = KeyBindings

    def run(self) -> None:
        kb = self.KeyBindings()
        session = self.PromptSession(key_bindings=kb, enable_history_search=True)
        store = self.ctx.macro_store

        from prompt_toolkit.keys import Keys

        @kb.add(Keys.Any)
        def _(event):
            """
            For printable keys: only intercept when a real binding will fire.
            Otherwise, insert the typed character so normal typing works.
            """
            buf = event.app.current_buffer
            ch = event.data  # '' for non-printables

            # Try to fire ONLY when: keys enabled, line empty, and printable char
            if ch and not buf.text and store.keys_enabled:
                script = resolve_bound_script(store, ch)
                if getattr(store, "keys_debug", False):
                    print(f"[#] any key='{ch}' -> {'hit' if bool(script) else 'miss'}")

                if script:
                    event.prevent_default()
                    buf.reset()
                    self.ctx.run_script(script)
                    return

            # Not handled -> INSERT the character so typing works
            if ch:
                event.app.current_buffer.insert_text(ch)

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
                    buf = event.app.current_buffer
                    if not store.keys_enabled or buf.text:
                        return  # do not intercept; let default behavior occur
                    script = resolve_bound_script(store, _n)
                    if getattr(store, "keys_debug", False):
                        print(f"[#] named key='{_n}' -> {'hit' if bool(script) else 'miss'}")
                    if script:
                        event.prevent_default()
                        buf.reset()
                        self.ctx.run_script(script)
            except Exception:
                pass

        while True:
            try:
                line = session.prompt("> ")
            except (EOFError, KeyboardInterrupt):
                print("")
                break
            if self.ctx.dispatch_line(line):
                break
