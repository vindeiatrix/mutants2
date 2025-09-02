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

        from prompt_toolkit.keys import Keys

        @kb.add(Keys.Any, eager=True)
        def _(event):
            """Printable keys: fire a macro only when the line is empty and a binding exists.
            Otherwise, insert the typed character so normal typing works."""
            store = self.ctx.macro_store
            buf = event.app.current_buffer
            ch = event.data  # printable char or '' for non-printables

            if ch and store.keys_enabled and not buf.text:
                script = resolve_bound_script(store, ch)
                if getattr(store, "keys_debug", False):
                    print(f"[#] key='{ch}' -> {'hit' if bool(script) else 'miss'}")

                if script:
                    # No prevent_default in PTK 3.x. Because this handler is eager,
                    # default insertion won’t run; we just clear the line and execute.
                    buf.reset()
                    self.ctx.run_script(script)   # expand + dispatch each subcommand
                    return

            # Not handled: insert the character so normal typing works.
            if ch:
                buf.insert_text(ch)

        while True:
            try:
                line = session.prompt("> ")
            except (EOFError, KeyboardInterrupt):
                print("")
                break
            if self.ctx.dispatch_line(line):
                break
