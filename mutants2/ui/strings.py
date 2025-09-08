from .theme import yellow

GET_WHAT = "What do you want to get?"
DROP_WHAT = "What do you want to drop?"
NOT_ENOUGH_IONS_PORTAL = "You don't have enough ions to create a portal."
CANT_SEE = "You can't see {0}."


def not_carrying(raw: str) -> str:
    """Return the yellow not-carrying message for ``raw``.

    ``raw`` is the exact subject as typed by the user with surrounding
    whitespace trimmed.
    """

    return yellow(f"You're not carrying {raw}.")
