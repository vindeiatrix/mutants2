import argparse
import os
import atexit
import sys

from .cli.shell import main

# Try to enable prompt_toolkit for richer key handling if available.
try:  # pragma: no cover
    import prompt_toolkit  # noqa: F401
except Exception:  # pragma: no cover
    prompt_toolkit = None

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


def _parse_args() -> tuple[bool, str | None, bool, bool]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="enable dev mode")
    parser.add_argument("--macro-profile", help="load macro profile on start")
    parser.add_argument("--ptk", action="store_true", help="force prompt_toolkit mode")
    parser.add_argument("--no-ptk", action="store_true", help="disable prompt_toolkit")
    args = parser.parse_args()
    dev = args.dev or os.environ.get("MUTANTS2_DEV") == "1"
    no_ptk = args.no_ptk or os.environ.get("MUTANTS2_NO_PTK") == "1"
    return dev, args.macro_profile, args.ptk, no_ptk


if __name__ == '__main__':
    dev_mode, macro_profile, force_ptk, no_ptk = _parse_args()
    if force_ptk and no_ptk:
        print("Cannot use both --ptk and --no-ptk")
        sys.exit(1)
    use_ptk = False
    if force_ptk:
        if prompt_toolkit is None:
            print("prompt_toolkit is required but not installed")
            sys.exit(1)
        use_ptk = True
    elif no_ptk:
        use_ptk = False
    else:
        use_ptk = prompt_toolkit is not None and sys.stdin.isatty()
    main(dev_mode=dev_mode, macro_profile=macro_profile, use_ptk=use_ptk)
