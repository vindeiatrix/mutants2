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


COLOR_HEADER = yellow
COLOR_ITEM = cyan
COLOR_DROP_ITEM = white

# ``blue`` previously represented a lighter variant used for exit descriptions.
# It is now an alias of ``COLOR_ITEM`` to remove that tone from the palette
# while keeping backwards compatibility.
blue = cyan

SEP = white("***")
