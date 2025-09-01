from __future__ import annotations

from ..engine import world, persistence, render
from ..engine.player import CLASS_LIST, CLASS_BY_NUM, CLASS_BY_NAME


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
        cmd = cmd_raw.strip().lower()
        if not cmd:
            continue
        if cmd.startswith("debug"):
            if not dev_mode:
                print("Debug commands are available only in dev mode.")
            else:
                parts = cmd.split()
                if len(parts) >= 2 and parts[1] == "shadow" and len(parts) == 3:
                    direction = parts[2]
                    if direction in {"north", "south", "east", "west"}:
                        p.senses.add_shadow(direction)
                        print("OK.")
                    else:
                        print("Invalid direction.")
                elif len(parts) >= 2 and parts[1] == "footsteps" and len(parts) == 3:
                    try:
                        p.senses.set_footsteps(int(parts[2]))
                        print("OK.")
                    except ValueError:
                        print("footsteps distance must be 1..4")
                elif len(parts) >= 2 and parts[1] == "clear":
                    p.senses.clear()
                    print("OK.")
                else:
                    print("Invalid debug command.")
            persistence.save(p)
            continue
        if cmd.startswith("loo"):
            render.render(p, w)
        elif cmd.startswith("nor"):
            if p.move("north", w):
                last_move = "north"
        elif cmd.startswith("sou"):
            if p.move("south", w):
                last_move = "south"
        elif cmd.startswith("eas"):
            if p.move("east", w):
                last_move = "east"
        elif cmd.startswith("wes"):
            if p.move("west", w):
                last_move = "west"
        elif cmd.startswith("las"):
            if last_move:
                p.move(last_move, w)
        elif cmd.startswith("tra"):
            parts = cmd.split()
            year = int(parts[1]) if len(parts) > 1 else None
            p.travel(w, year)
        elif cmd.startswith("cla"):
            changed = class_menu(p, in_game=True)
            if changed:
                render.render(p, w)
        elif cmd.startswith("exi"):
            persistence.save(p)
            break
        else:
            print("Commands: look, north, south, east, west, last, travel, class, exit")
        persistence.save(p)
