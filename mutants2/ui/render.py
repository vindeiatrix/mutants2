from .theme import yellow, SEP


def render_help_hint() -> None:
    """Print the standard help hint in yellow."""
    print(SEP)
    print(yellow("Type ? if you need assistance."))
