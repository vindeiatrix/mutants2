from __future__ import annotations

import re
import sys
from types import SimpleNamespace

from .repl import FallbackRepl, PtkRepl

from ..engine import world, persistence, render, items
from ..engine.player import CLASS_LIST, CLASS_BY_NUM, CLASS_BY_NAME
from ..engine.macros import MacroStore, resolve_bound_script
from .keynames import normalize_key
from ..ui.help import MACROS_HELP


DIRECTION_ALIASES = {
    "n": "north", "north": "north",
    "s": "south", "south": "south",
    "e": "east", "east": "east",
    "w": "west", "west": "west",
}


def is_single_key(s: str) -> bool:
    s = s.lower()
    if len(s) == 1:
        return True
    if s.startswith("f") and s[1:].isdigit():
        i = int(s[1:])
        return 1 <= i <= 12
    return s in {
        "up",
        "down",
        "left",
        "right",
        "home",
        "end",
        "pageup",
        "pagedown",
        "tab",
        "escape",
        "space",
    }


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


def main(*, dev_mode: bool = False, macro_profile: str | None = None, use_ptk: bool = False) -> None:
    p, ground, seeded = persistence.load()
    w = world.World(ground, seeded)
    macro_store = MacroStore()
    try:
        macro_store.load_profile("default")
    except FileNotFoundError:
        pass
    if macro_profile:
        try:
            macro_store.load_profile(macro_profile)
        except FileNotFoundError:
            pass
    last_move = None

    if p.clazz is None:
        class_menu(p, w, in_game=False)
    render.render(p, w)
    context = SimpleNamespace(macro_store=macro_store, running=True)

    def dispatch(line: str) -> bool:
        nonlocal last_move
        s = line.strip()
        parts = s.split()
        if not parts:
            return True
        cmd = parts[0].lower()
        args = parts[1:]

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

        if cmd == "help":
            topic = " ".join(args).strip().lower() if args else ""
            if topic in {"macros", "macro"}:
                print(MACROS_HELP)
            else:
                print("Commands: look, north, south, east, west, last, travel, class, inventory, get, drop, exit, macro, @name, do")
            return True
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
            persistence.save(p, w)
            return True
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
            changed = class_menu(p, w, in_game=True)
            if changed:
                render.render(p, w)
        elif cmd in {"inventory", "inv", "i"}:
            if p.inventory:
                for key, count in p.inventory.items():
                    print(f"{items.REGISTRY[key].name} x{count}")
            else:
                print("(empty)")
        elif cmd in {"get", "take"}:
            name = " ".join(args)
            item = items.find_by_name(name)
            ground_key = w.ground_item(p.year, p.x, p.y)
            if item and ground_key == item.key:
                w.set_ground_item(p.year, p.x, p.y, None)
                p.inventory[item.key] = p.inventory.get(item.key, 0) + 1
                print(f"You pick up {item.name}.")
                render.render(p, w)
            else:
                print("You don't see that here.")
        elif cmd == "drop":
            name = " ".join(args)
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
                render.render(p, w)
        elif cmd == "exit":
            context.running = False
            return False
        else:
            if macro_store.keys_enabled and is_single_key(s):
                script = resolve_bound_script(macro_store, s.lower())
                if script:
                    macro_store.expand_and_run_script(script, dispatch)
                    return True
            print("Unknown command.")
            return False
        persistence.save(p, w)
        return True

    def dispatch_line(cmd_raw: str) -> None:
        cmd_raw = cmd_raw.strip()
        if not cmd_raw:
            return
        m = re.fullmatch(r"/macro\s+(\S+)\s+\{(.+)\}\s*", cmd_raw)
        if m:
            key = normalize_key(m.group(1))
            if key is None:
                print("Unknown key name.")
            else:
                macro_store.bind(key, m.group(2))
            return
        if cmd_raw.startswith("press "):
            key = normalize_key(cmd_raw[6:].strip())
            if key is None:
                print("Unknown key name.")
            else:
                macro_store.press(key, dispatch)
            return
        if cmd_raw.startswith("@"):
            content = cmd_raw[1:].strip()
            if content:
                parts = content.split()
                name = parts[0]
                args = parts[1:]
                macro_store.run_named(name, args, dispatch)
        elif cmd_raw.startswith("do "):
            script = cmd_raw[3:].strip()
            macro_store.run(script, [], dispatch)
        elif cmd_raw.startswith("macro"):
            rest = cmd_raw[5:].strip()
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
                    macro_store.run_named(name, args, dispatch)
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
            elif rest.startswith("bind "):
                after = rest[5:]
                if "=" in after:
                    key_part, script = after.split("=", 1)
                    key = normalize_key(key_part.strip())
                    if key is None:
                        print("Unknown key name.")
                    else:
                        macro_store.bind(key, script.strip())
                else:
                    print("Usage: macro bind <key> = <script>")
            elif rest.startswith("unbind "):
                key = normalize_key(rest[7:].strip())
                if key is None:
                    print("Unknown key name.")
                else:
                    macro_store.unbind(key)
            elif rest == "bindings":
                for k, v in sorted(macro_store.bindings().items()):
                    print(f"{k} = {v}")
            elif rest.startswith("keys "):
                sub = rest[5:].strip().lower()
                if sub in {"on", "off"}:
                    macro_store.keys_enabled = sub == "on"
                elif sub.startswith("debug "):
                    val = sub[6:].strip()
                    if val in {"on", "off"}:
                        macro_store.keys_debug = val == "on"
                    else:
                        print("Usage: macro keys debug on|off")
                elif sub == "status":
                    print(
                        f"mode={macro_store.repl_mode}, keys_enabled={macro_store.keys_enabled}, debug={macro_store.keys_debug}"
                    )
                else:
                    print("Usage: macro keys on|off | debug on|off | status")
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
        else:
            dispatch(cmd_raw)
        if not context.running:
            return

    context.dispatch_line = dispatch_line
    context.run_script = lambda script: macro_store.expand_and_run_script(script, dispatch)

    repl = PtkRepl(context) if use_ptk else FallbackRepl(context)
    repl.run()

