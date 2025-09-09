NO_COLOR = False  # honor an env/config flag if you already have one


def green(s: str) -> str:
    return s if NO_COLOR else f"\x1b[32m{s}\x1b[0m"


def cyan(s: str) -> str:
    return s if NO_COLOR else f"\x1b[36m{s}\x1b[0m"


def yellow(s: str) -> str:
    return s if NO_COLOR else f"\x1b[33m{s}\x1b[0m"


def red(s: str) -> str:
    return s if NO_COLOR else f"\x1b[31m{s}\x1b[0m"


def white(s: str) -> str:
    return s if NO_COLOR else f"\x1b[37m{s}\x1b[0m"


# Core semantic colors -------------------------------------------------------
# ``COLOR_HEADER`` drives section titles such as "On the ground lies:",
# cardinal direction labels, and the stats inventory header/list.  ``COLOR_ITEM``
# is used for ground item names and exit descriptions.
COLOR_HEADER = yellow
COLOR_ITEM = cyan

# ``blue`` previously represented a lighter variant used for exit descriptions.
# It is now an alias of ``COLOR_ITEM`` to remove that tone from the palette
# while keeping backwards compatibility.
blue = cyan

SEP = white("***")

__all__ = [
    "NO_COLOR",
    "green",
    "cyan",
    "yellow",
    "red",
    "white",
    "COLOR_HEADER",
    "COLOR_ITEM",
    "blue",
    "SEP",
]
