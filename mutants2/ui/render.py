from .theme import yellow, SEP


def render_help_hint() -> None:
    """Print the standard help hint in yellow."""
    print(SEP)
    print(yellow("Type ? if you need assistance."))


def print_yell(mon) -> str:
    """Return the yell line for a monster."""
    name = mon.get("name") or mon.get("key")
    return f"{name} yells at you!"
