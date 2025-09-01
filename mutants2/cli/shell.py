from __future__ import annotations

from ..engine import world, persistence, render
from ..engine.player import CLASS_LIST, CLASS_BY_NUM, CLASS_BY_NAME


DIRECTION_ALIASES = {
    "n": "north", "north": "north",
    "s": "south", "south": "south",
    "e": "east", "east": "east",
    "w": "west", "west": "west",
}


def class_menu(p, *, in_game: bool) -> bool:
    """Show the class selection menu.

    Returns ``True`` if the player's class was changed, ``False`` otherwise.
    ``in_game`` distinguishes between startup and the ``class`` command.
    """
    print("Choose your class:")
    for i, name in enumerate(CLASS_LIST, 1):
        print(f"{i}. {name}")
    while True:
        try:
            s = input("class> ").strip().lower()
        except EOFError:
            s = ""
        if not s:
            continue
        if s in {"back", "b"}:
            if in_game:
                return False
            print("Pick a class to begin.")
            continue
        if s.startswith("debug"):
            print("Debug commands are available only in dev mode (in-game).")
            continue
        if s in CLASS_BY_NUM:
            picked = CLASS_BY_NUM[s]
        elif s in CLASS_BY_NAME:
            picked = CLASS_BY_NAME[s]
        else:
            print("Invalid selection.")
            continue
        p.clazz = picked
        persistence.save(p)
        return True


def main(*, dev_mode: bool = False) -> None:
    w = world.World()
    p = persistence.load()
    last_move = None
    if p.clazz is None:
        class_menu(p, in_game=False)
    render.render(p, w)
    while True:
        try:
            cmd_raw = input("> ")
        except EOFError:
            cmd_raw = ""
        parts = cmd_raw.strip().split()
        if not parts:
            continue
        cmd = parts[0].lower()
        args = parts[1:]

        # Resolve direction aliases and handle traditional prefixes.
        direction = DIRECTION_ALIASES.get(cmd)
        if direction is None:
            if cmd.startswith("nor"):
                direction = "north"
            elif cmd.startswith("sou"):
                direction = "south"
            elif cmd.startswith("eas"):
                direction = "east"
            elif cmd.startswith("wes"):
                direction = "west"

        if cmd == "debug":
            if not dev_mode:
                print("Debug commands are available only in dev mode.")
            else:
                if args and args[0] == "shadow" and len(args) == 2:
                    direction = args[1]
                    if direction in {"north", "south", "east", "west"}:
                        p.senses.add_shadow(direction)
                        print("OK.")
                    else:
                        print("Invalid direction.")
                elif args and args[0] == "footsteps" and len(args) == 2:
                    try:
                        p.senses.set_footsteps(int(args[1]))
                        print("OK.")
                    except ValueError:
                        print("footsteps distance must be 1..4")
                elif args and args[0] == "clear" and len(args) == 1:
                    p.senses.clear()
                    print("OK.")
                else:
                    print("Invalid debug command.")
            persistence.save(p)
            continue
        elif cmd == "look":
            render.render(p, w)
        elif direction in {"north", "south", "east", "west"}:
            if p.move(direction, w):
                last_move = direction
            render.render(p, w)
        elif cmd == "last":
            if last_move:
                p.move(last_move, w)
                render.render(p, w)
        elif cmd == "travel":
            year = int(args[0]) if args else None
            p.travel(w, year)
        elif cmd == "class":
            changed = class_menu(p, in_game=True)
            if changed:
                render.render(p, w)
        elif cmd == "exit":
            persistence.save(p)
            break
        else:
            print("Commands: look, north, south, east, west, last, travel, class, exit")
        persistence.save(p)
