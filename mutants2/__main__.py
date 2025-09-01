import argparse
import os
import atexit

from .cli.shell import main

# Enable command history and line editing if ``readline`` is available. The
# history is persisted across sessions in ``~/.mutants2/history``. Importing
# ``readline`` has the side effect of enabling arrow key navigation in
# interactive terminals, but this block is designed to fail silently on
# platforms where ``readline`` is unavailable so non-interactive runs (such as
# tests) continue to function.
try:  # pragma: no cover - behaviour depends on platform availability
    import readline

    histdir = os.path.expanduser("~/.mutants2")
    os.makedirs(histdir, exist_ok=True)
    histfile = os.path.join(histdir, "history")
    try:
        readline.read_history_file(histfile)
    except FileNotFoundError:
        pass
    readline.set_history_length(2000)
    atexit.register(readline.write_history_file, histfile)
except Exception:  # pragma: no cover - best-effort only
    pass


def _parse_args() -> bool:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="enable dev mode")
    args = parser.parse_args()
    return args.dev or os.environ.get("MUTANTS2_DEV") == "1"


if __name__ == '__main__':
    dev_mode = _parse_args()
    main(dev_mode=dev_mode)
