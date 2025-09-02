from __future__ import annotations

from types import SimpleNamespace

from ..engine import world, persistence, items
from ..engine.render import render_room_view
from ..engine.player import CLASS_LIST, CLASS_BY_NUM, CLASS_BY_NAME
from ..engine.macros import MacroStore
from ..ui.help import MACROS_HELP, ABBREVIATIONS_NOTE


CANON = {
    "look": "look",
    "travel": "travel",
    "class": "class",
    "last": "last",
    "exit": "exit",
    "inventory": "inventory",
    "drop": "drop",
    "get": "get",
    "take": "get",
    "macro": "macro",
    "help": "help",
    "do": "do",
    "debug": "debug",
    "north": "north",
    "south": "south",
    "east": "east",
    "west": "west",
}

EXPLICIT_ALIASES = {
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "inv": "inventory",
}

NONDIR_CANON = [c for c in CANON if c not in ("north", "south", "east", "west")]


def resolve_command(token: str) -> str | None:
    t = token.strip().lower()
    if not t:
        return None
    if t in EXPLICIT_ALIASES:
        return EXPLICIT_ALIASES[t]
    if t in CANON:
        return CANON[t]
    if any(w.startswith(t) for w in ("north", "south", "east", "west")):
        return None
    if len(t) >= 3:
        matches = {CANON[c] for c in NONDIR_CANON if c.startswith(t)}
        if len(matches) == 1:
            return next(iter(matches))
    return None


def class_menu(p, w, *, in_game: bool) -> bool:
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
        persistence.save(p, w)
        return True


def make_context(*, dev: bool = False):
    p, ground, seeded = persistence.load()
    w = world.World(ground, seeded)
    macro_store = MacroStore()
    try:
        macro_store.load_profile("default")
    except FileNotFoundError:
        pass
    last_move = None

    if p.clazz is None:
        class_menu(p, w, in_game=False)
    render_room_view(p, w)
    context = SimpleNamespace(macro_store=macro_store, running=True)

    def handle_macro(rest: str) -> None:
        if rest.startswith("add "):
            after = rest[4:]
            if "=" in after:
                name_part, script = after.split("=", 1)
                macro_store.add(name_part.strip(), script.strip())
            else:
                print("Usage: macro add <name> = <script>")
        elif rest.startswith("run "):
            parts = rest[4:].split()
            if parts:
                name = parts[0]
                args = parts[1:]
                macro_store.run_named(name, args, dispatch_macro)
        elif rest == "list":
            for n in macro_store.list():
                print(n)
        elif rest.startswith("show "):
            name = rest[5:].strip()
            if name in macro_store.list():
                print(macro_store.get(name))
            else:
                print("No such macro")
        elif rest.startswith("rm "):
            macro_store.remove(rest[3:].strip())
        elif rest == "clear":
            confirm = input("Clear all macros? type yes to confirm: ").strip().lower()
            if confirm == "yes":
                macro_store.clear()
        elif rest.startswith("echo "):
            val = rest[5:].strip().lower()
            macro_store.echo = val == "on"
        elif rest.startswith("save "):
            profile = rest[5:].strip()
            macro_store.save_profile(profile)
        elif rest.startswith("load "):
            profile = rest[5:].strip()
            try:
                macro_store.load_profile(profile)
            except FileNotFoundError:
                print("No such profile")
        elif rest == "profiles":
            for n in macro_store.list_profiles():
                print(n)
        else:
            print("Invalid macro command.")

    def handle_travel(args: list[str]) -> bool:
        if args:
            try:
                year = int(args[0])
            except ValueError:
                print("Invalid year.")
                return False
        else:
            year = None
        p.travel(w, year)
        return True

    def handle_command(cmd: str, args: list[str]) -> bool:
        nonlocal last_move
        if cmd == "look":
            render_room_view(p, w)
        elif cmd == "last":
            if last_move:
                p.move(last_move, w)
            render_room_view(p, w)
        elif cmd == "class":
            changed = class_menu(p, w, in_game=True)
            if changed:
                render_room_view(p, w)
        elif cmd == "inventory":
            if p.inventory:
                for key, count in p.inventory.items():
                    print(f"{items.REGISTRY[key].name} x{count}")
            else:
                print("(empty)")
        elif cmd == "get":
            if not args:
                ground_key = w.ground_item(p.year, p.x, p.y)
                if ground_key:
                    name = items.REGISTRY[ground_key].name
                    print(f"On the ground: {name}")
                else:
                    print("On the ground: (nothing)")
                ground_key = None
            if args:
                ground_key = w.ground_item(p.year, p.x, p.y)
                ground_names = []
                if ground_key:
                    ground_names.append(items.REGISTRY[ground_key].name)
                name, amb = items.resolve_item_prefix(" ".join(args), ground_names)
                if amb:
                    print("Ambiguous: " + ", ".join(amb))
                elif not name:
                    print(f'No item here matching "{' '.join(args)}".')
                else:
                    item = items.find_by_name(name)
                    if item and ground_key == item.key:
                        w.set_ground_item(p.year, p.x, p.y, None)
                        p.inventory[item.key] = p.inventory.get(item.key, 0) + 1
                        print(f"You pick up {item.name}.")
                    else:
                        print("You don't see that here.")
        elif cmd == "drop":
            if not args:
                if p.inventory:
                    print("Inventory: " + ", ".join(
                        f"{items.REGISTRY[k].name} x{c}" for k, c in p.inventory.items()
                    ))
                else:
                    print("(inventory empty)")
            else:
                inv_names = [items.REGISTRY[k].name for k in p.inventory]
                name, amb = items.resolve_item_prefix(" ".join(args), inv_names)
                if amb:
                    print("Ambiguous: " + ", ".join(amb))
                elif not name:
                    print(f'No item in inventory matching "{' '.join(args)}".')
                else:
                    item = items.find_by_name(name)
                    if not item or p.inventory.get(item.key, 0) == 0:
                        print("You don't have that.")
                    elif w.ground_item(p.year, p.x, p.y):
                        print("You can only drop when the ground is empty here.")
                    else:
                        p.inventory[item.key] -= 1
                        if p.inventory[item.key] == 0:
                            del p.inventory[item.key]
                        w.set_ground_item(p.year, p.x, p.y, item.key)
                        print(f"You drop {item.name}.")
        elif cmd == "help":
            topic = " ".join(args).strip().lower() if args else ""
            if topic in {"macros", "macro"}:
                print(MACROS_HELP)
            else:
                print("Commands: look, north, south, east, west, last, travel, class, inventory, get, drop, exit, macro, @name, do")
                print()
                print(ABBREVIATIONS_NOTE)
        elif cmd == "debug":
            if not dev:
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
        elif cmd in {"north", "south", "east", "west"}:
            if p.move(cmd, w):
                last_move = cmd
            render_room_view(p, w)
        elif cmd == "travel":
            ok = handle_travel(args)
            if ok:
                render_room_view(p, w)
        elif cmd == "exit":
            print("Goodbye.")
            context.running = False
            return False
        else:
            print("Unknown command.")
            return False
        persistence.save(p, w)
        return True

    def dispatch_macro(cmd_raw: str) -> bool:
        cmd_raw = cmd_raw.strip()
        if not cmd_raw:
            return True
        if cmd_raw.startswith("@"):
            content = cmd_raw[1:].strip()
            if content:
                parts = content.split()
                name = parts[0]
                args = parts[1:]
                macro_store.run_named(name, args, dispatch_macro)
            return True
        if cmd_raw.startswith("do "):
            script = cmd_raw[3:].strip()
            macro_store.run(script, [], dispatch_macro)
            return True
        parts = cmd_raw.split(maxsplit=1)
        head = parts[0]
        tail = parts[1] if len(parts) > 1 else ""
        cmd = resolve_command(head)
        if cmd is None:
            print("Unknown command.")
            return False
        if cmd == "macro":
            handle_macro(tail)
            return True
        args = tail.split()
        return handle_command(cmd, args)

    def dispatch_line(line: str) -> bool:
        dispatch_macro(line)
        if not context.running:
            return True
        return False

    context.run_script = lambda script: macro_store.expand_and_run_script(script, dispatch_macro)
    context.dispatch_line = dispatch_line
    context.try_dispatch_builtin = dispatch_macro

    return context

