import os
import atexit

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

from .main import main

if __name__ == "__main__":
    main()
