import argparse
import os
import atexit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()

    dev = args.dev or os.environ.get("MUTANTS2_DEV") == "1"

    # Optional: readline history
    try:  # pragma: no cover - depends on platform availability
        import readline  # type: ignore

        histdir = os.path.expanduser("~/.mutants2")
        os.makedirs(histdir, exist_ok=True)
        histfile = os.path.join(histdir, "history")
        try:
            readline.read_history_file(histfile)
        except FileNotFoundError:
            pass
        atexit.register(readline.write_history_file, histfile)
    except Exception:  # pragma: no cover - best effort only
        pass

    from mutants2.cli.shell import make_context

    ctx = make_context(dev=dev)

    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if ctx.dispatch_line(line):
            break


if __name__ == "__main__":  # pragma: no cover
    main()

