from __future__ import annotations


class FeedbackBus:
    """A tiny feedback bus collecting messages for rendering."""

    def __init__(self) -> None:
        self._events: list[tuple[str, str]] = []

    def push(self, kind: str, text: str, **meta) -> None:  # noqa: D401 - thin shim
        self._events.append((kind, text))

    def drain(self) -> list[tuple[str, str]]:
        events = list(self._events)
        self._events.clear()
        return events


def build_context() -> dict:
    """Build the minimal runtime context for the REPL."""
    return {"feedback_bus": FeedbackBus()}


def render_frame(ctx: dict) -> None:
    """Render any drained feedback lines. Placeholder for full renderer."""
    bus: FeedbackBus = ctx["feedback_bus"]
    for _kind, text in bus.drain():
        print(text)
