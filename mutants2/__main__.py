from __future__ import annotations

import argparse
import os
import atexit
import time


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
    from mutants2.engine.types import MonsterRec
    from mutants2.types import TileKey, ItemInstance
    from mutants2.engine.render import render_room_view
    from mutants2.engine.gen import daily_topup_if_needed
    from mutants2.engine import loop

    p, ground, monsters, seeded, save = persistence.load()
    ground_map: dict[TileKey, list[ItemInstance]] = ground
    monsters_map: dict[TileKey, list[MonsterRec]] = monsters
    w = world_mod.World(ground_map, seeded, monsters_map, global_seed=save.global_seed)

    if p.clazz is None:
        w.reset_all_aggro()
        class_menu(p, w, save, None, in_game=False)

    placed = daily_topup_if_needed(w, p, save)
    if dev and placed:
        print(f"[dev] Daily top-up placed {placed} items.")

    yells = w.on_entry_aggro_check(
        p.year, p.x, p.y, p, seed_parts=(save.global_seed, w.turn)
    )
    render_room_view(p, w)
    for line in yells:
        print(line)

    save.next_upkeep_tick = time.monotonic() + loop.TICK_SECONDS
    ctx = make_context(p, w, save, dev=dev)
    ctx.tick_handle = loop.start_realtime_tick(p, w, save, ctx)
    try:
        while True:
            try:
                line = input("")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if ctx.dispatch_line(line):
                break
    finally:
        loop.stop_realtime_tick(getattr(ctx, "tick_handle", None))


if __name__ == "__main__":  # pragma: no cover
    main()
