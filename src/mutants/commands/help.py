from __future__ import annotations
from mutants.repl.help import render_help


def register(dispatch, ctx):
    bus = ctx["feedback_bus"]

    def _help(arg: str = "") -> None:
        text = render_help(dispatch)
        bus.push("SYSTEM/OK", text)

    dispatch.register("help", _help)
    dispatch.alias("h", "help")
