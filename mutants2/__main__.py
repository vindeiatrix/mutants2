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

    from mutants2.cli.shell import make_context, class_menu
    from mutants2.engine import persistence, world as world_mod
    from mutants2.engine.render import render_room_view
    from mutants2.engine.gen import daily_topup_if_needed

    p, ground, monsters, seeded, save = persistence.load()
    w = world_mod.World(ground, seeded, monsters, global_seed=save.global_seed)

    if p.clazz is None:
        class_menu(p, w, save, in_game=False)

    placed = daily_topup_if_needed(w, p, save)
    if dev and placed:
        print(f"[dev] Daily top-up placed {placed} items.")

    render_room_view(p, w)

    ctx = make_context(p, w, save, dev=dev)

    while True:
        try:
            line = input("")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if ctx.dispatch_line(line):
            break


if __name__ == "__main__":  # pragma: no cover
    main()

