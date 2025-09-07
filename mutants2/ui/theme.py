NO_COLOR = False  # honor an env/config flag if you already have one


def red(s):
    return s if NO_COLOR else f"\x1b[31m{s}\x1b[0m"


def green(s):
    return s if NO_COLOR else f"\x1b[32m{s}\x1b[0m"


def cyan(s):
    return s if NO_COLOR else f"\x1b[36m{s}\x1b[0m"


def yellow(s):
    return s if NO_COLOR else f"\x1b[33m{s}\x1b[0m"


def white(s):
    return s if NO_COLOR else f"\x1b[37m{s}\x1b[0m"


SEP = white("***")
