from __future__ import annotations

from types import SimpleNamespace
import datetime
from typing import Mapping, cast

from ..engine import persistence, items, monsters
from ..engine.render import render_room_view
from ..engine import render as render_mod
from ..engine.player import CLASS_LIST, CLASS_BY_NUM, CLASS_BY_NAME
from ..engine.gen import daily_topup_if_needed
from ..engine.macros import MacroStore
from ..engine.types import Direction
from ..engine.world import ALLOWED_CENTURIES
from ..ui.help import MACROS_HELP, ABBREVIATIONS_NOTE, COMMANDS_HELP, USAGE
from ..ui.strings import GET_WHAT, DROP_WHAT
from ..ui.theme import red, SEP, yellow, cyan, white
from ..ui.render import render_help_hint
from .input import gerundize


NONDIR_CMDS = {
    "look": "look",
    "travel": "travel",
    "class": "class",
    "last": "last",
    "exit": "exit",
    "inventory": "inventory",
    "drop": "drop",
    "get": "get",
    "take": "get",
    "convert": "convert",
    "macro": "macro",
    "help": "help",
    "do": "do",
    "status": "status",
    "rest": "rest",
    "attack": "attack",
    "debug": "debug",
}

TURN_CMDS = {
    "north",
    "south",
    "east",
    "west",
    "travel",
    "get",
    "drop",
    "convert",
    "attack",
    "rest",
    "look",
}

DIR_FULL: tuple[Direction, ...] = ("north", "south", "east", "west")
DIR_1: Mapping[str, Direction] = {
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
}


def parse_dir_any_prefix(tok: str) -> Direction | None:
    """Return a direction if tok is 1..full prefix of exactly one dir."""
    t = tok.strip().lower()
    if not t:
        return None
    if t in DIR_1:
        return DIR_1[t]
    matches: list[Direction] = [d for d in DIR_FULL if d.startswith(t)]
    if len(matches) == 1:
        return matches[0]
    return None


def resolve_command(token: str) -> str | None:
    t = token.lower()
    if not t:
        return None
    if t == "x":
        return "class"
    if t in DIR_1:
        return DIR_1[t]
    if t in DIR_FULL:
        return t
    for canon, target in NONDIR_CMDS.items():
        L = len(canon)
        kmin = min(3, L)
        if kmin <= len(t) <= L and canon.startswith(t):
            return target
    return None


def class_menu(p, w, save, *, in_game: bool) -> bool:
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
        prof = save.profiles.get(picked)
        if prof:
            p.year = int(prof.get("year", 2000))
            p.positions = {
                int(y): (v.get("x", 0), v.get("y", 0))
                for y, v in prof.get("positions", {}).items()
            }
            p.inventory = {k: int(v) for k, v in prof.get("inventory", {}).items()}
            p.max_hp = int(prof.get("max_hp", p.max_hp))
            p.hp = int(prof.get("hp", p.max_hp))
            p.ions = int(prof.get("ions", 0))
        else:
            p.year = ALLOWED_CENTURIES[0]
            p.positions = {c: (0, 0) for c in ALLOWED_CENTURIES}
            p.inventory.clear()
            p.hp = p.max_hp = 10
            p.ions = 0
        w.year(p.year)
        p.clazz = picked
        persistence.save(p, w, save)
        return True


def make_context(p, w, save, *, dev: bool = False):
    macro_store = MacroStore()
    try:
        macro_store.load_profile(p.clazz or "default")
    except FileNotFoundError:
        pass
    last_move = None

    PLAYER_DMG = 2
    MONSTER_DMG = 1

    context = SimpleNamespace(
        macro_store=macro_store,
        running=True,
        player=p,
        world=w,
        save=save,
        _arrivals_this_tick=[],
        _footsteps_event=None,
        _entry_yells=[],
        _pre_shadow_lines=[],
        _needs_render=False,
        _last_turn_consumed=False,
        _suppress_room_render=False,
    )

    def render_usage(cmd: str) -> None:
        for line in USAGE.get(cmd, []):
            print(line)

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
        if not args:
            render_usage("travel")
            context._suppress_room_render = True
            return False
        try:
            year_input = int(args[0])
        except ValueError:
            print("Invalid year.")
            context._suppress_room_render = True
            return False
        if year_input < ALLOWED_CENTURIES[0] or year_input > ALLOWED_CENTURIES[-1]:
            print(yellow("You can only travel from year 2000 to 2200!"))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        target = max(c for c in ALLOWED_CENTURIES if c <= year_input)
        p.travel(w, target)
        print(white(f"ZAAAAPPPPP!! You've been sent to the year {target} A.D."))
        context._suppress_room_render = True
        return True

    def handle_get(args: list[str]) -> bool:
        if not args:
            print(GET_WHAT)
            return False
        ground = [it.name for it in w.items_on_ground(p.year, p.x, p.y)]
        name = items.first_prefix_match(" ".join(args), ground)
        if not name:
            print(f'No item here matching "{" ".join(args)}".')
            return False
        p.pick_up(name, w)
        print(f"You pick up {name}.")
        return False

    def handle_drop(args: list[str]) -> bool:
        if not args:
            print(DROP_WHAT)
            return False
        inv_names = p.inventory_names_in_order()
        name = items.first_prefix_match(" ".join(args), inv_names)
        if not name:
            print(f'No item in inventory matching "{" ".join(args)}".')
            return False
        ok, msg = p.drop_to_ground(name, w)
        print(f"You drop {name}." if ok else (msg or "You can’t drop that here."))
        return False

    def handle_convert(args: list[str]) -> bool:
        if not args:
            render_usage("convert")
            context._suppress_room_render = True
            return False
        raw = " ".join(args)
        canon = items.canon_item_key(raw)
        key_match = None
        for k in p.inventory.keys():
            if items.canon_item_key(k).startswith(canon) or items.canon_item_key(items.display_name(k)).startswith(canon):
                key_match = k
                break
        if not key_match:
            print(yellow("***"))
            print(yellow(f"You're not carrying a {raw}."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        item = p.convert_item(items.display_name(key_match))
        if not item:
            render_help_hint()
            return False
        print(SEP)
        print(yellow(f"The {item.name} vanishes with a flash!"))
        print(yellow(f"You convert the {item.name} into {item.ion_value:,} ions."))
        context._needs_render = False
        context._suppress_room_render = True
        return True

    def handle_look(args: list[str]) -> bool:
        if not args:
            yells = w.on_entry_aggro_check(
                p.year, p.x, p.y, p, seed_parts=(save.global_seed, w.turn)
            )
            if yells:
                context._entry_yells.extend(yells)
            context._needs_render = True
            return False

        q = " ".join(args).strip().lower()

        here_monsters = [
            monsters.REGISTRY[m["key"]].name for m in w.monsters_here(p.year, p.x, p.y)
        ]
        mname = monsters.first_mon_prefix(q, here_monsters)
        if mname:
            print(f"It's a {mname}.")
            return False

        inv_names = p.inventory_names_in_order()
        iname = items.first_prefix_match(q, inv_names)
        if iname:
            print(items.describe(iname))
            return False
        ground_names = [it.name for it in w.items_on_ground(p.year, p.x, p.y)]
        gname = items.first_prefix_match(q, ground_names)
        if gname:
            print(yellow("***"))
            print(yellow(f"It looks like a lovely {gname}!"))
            return False

        d = parse_dir_any_prefix(q)
        if d:
            if not w.is_open(p.year, p.x, p.y, d):
                print("You can't look that way.")
                return False
            ax, ay = w.step(p.x, p.y, d)
            text = render_mod.render_room_at(
                w,
                p.year,
                ax,
                ay,
                include_shadows=False,
            )
            print(text)
            return False

        print("You can't look that way.")
        return False

    def handle_attack() -> None:
        m = w.monster_here(p.year, p.x, p.y)
        if not m:
            print("There is nothing here to attack.")
            return
        name = cast(str, m.get("name"))
        dead = w.damage_monster(p.year, p.x, p.y, PLAYER_DMG)
        if dead:
            print(f"You defeat the {name}.")
            context._needs_render = False
            context._suppress_room_render = True
            return
        p.take_damage(MONSTER_DMG)
        print(f"The {name} hits you (-{MONSTER_DMG} HP). (HP: {p.hp}/{p.max_hp})")
        if p.is_dead():
            print("You have died.")
            p.heal_full()
            p.positions[p.year] = (0, 0)
            w.reset_aggro_in_year(p.year)
            context._arrivals_this_tick = []
        context._needs_render = False
        context._suppress_room_render = True

    def handle_rest() -> None:
        if w.monster_here(p.year, p.x, p.y):
            print("You can’t rest while a monster is here.")
            return
        p.heal_full()
        print(f"You rest and recover. (HP: {p.hp}/{p.max_hp})")

    def handle_status() -> None:
        print(
            f"Class: {p.clazz} | HP: {p.hp}/{p.max_hp} | Year: {p.year} @ {p.x}E : {p.y}N"
        )
        print(f"Total Ions: {p.ions}")

    def handle_command(cmd: str, args: list[str]) -> bool:
        nonlocal last_move
        turn = False
        if cmd == "look":
            handle_look(args)
            turn = True
        elif cmd == "last":
            moved = False
            if last_move:
                moved = p.move(last_move, w)
                if p._last_move_struck_back:
                    context._suppress_room_render = True
            if moved or p._last_move_struck_back:
                turn = True
            context._needs_render = True
        elif cmd == "class":
            macro_store.save_profile(p.clazz or "default")
            persistence.save(p, w, save)
            w.reset_all_aggro()
            changed = class_menu(p, w, save, in_game=True)
            if changed:
                macro_store.load_profile(p.clazz or "default")
                yells = w.on_entry_aggro_check(
                    p.year, p.x, p.y, p, seed_parts=(save.global_seed, w.turn)
                )
                render_room_view(p, w, context)
                for line in yells:
                    print(line)
        elif cmd == "inventory":
            total = p.inventory_weight_lbs()
            print(
                yellow(
                    f"You are carrying the following items: (Total Weight: {total} LB's)"
                )
            )
            if p.inventory:
                names: list[str] = []
                for key, count in p.inventory.items():
                    names.extend([items.REGISTRY[key].name] * count)
                line = ", ".join(names) + "."
                print(cyan(line))
            else:
                print("(empty)")
        elif cmd == "get":
            handle_get(args)
            turn = True
        elif cmd == "drop":
            handle_drop(args)
            turn = True
        elif cmd == "convert":
            if handle_convert(args):
                turn = True
        elif cmd == "attack":
            handle_attack()
            turn = True
        elif cmd == "rest":
            handle_rest()
            turn = True
        elif cmd == "status":
            handle_status()
        elif cmd == "help":
            if args and args[0].lower() == "debug":
                print(
                    """Debug commands:
  debug item add <name|key> [count]   Add item(s) to current room's ground.
  debug item clear                    Remove all ground items here.
  debug item list                     Show raw ground items here.
  debug mon here                      Toggle a Mutant on this tile.
  debug mon spawn <n>                 Spawn n Mutants near the player (dev).
  debug mon count                     Count monsters in current year.
  debug today YYYY-MM-DD              Set synthetic 'today' (dev date).
  debug today clear                   Clear synthetic date.
  debug topup                         Run daily item top-up now.
  macro keys debug on|off             Toggle macro key debug (if available).
"""
                )
            else:
                topic = " ".join(args).strip().lower() if args else ""
                if topic in {"macros", "macro"}:
                    print(MACROS_HELP)
                else:
                    print(COMMANDS_HELP)
                    print()
                    print(ABBREVIATIONS_NOTE)
        elif cmd == "debug":
            if not dev:
                print("Debug commands are available only in dev mode.")
            else:
                if args[:2] == ["item", "add"] and len(args) >= 3:
                    name_or_key = args[2]
                    count = int(args[3]) if len(args) >= 4 and args[3].isdigit() else 1
                    key = items.resolve_key_prefix(name_or_key)
                    if not key:
                        print("Unknown item.")
                        return False
                    for _ in range(count):
                        w.add_ground_item(p.year, p.x, p.y, key)
                    print(f"OK: added {count} x {items.display_name(key)}.")
                elif args[:2] == ["item", "clear"]:
                    w.ground.pop((p.year, p.x, p.y), None)
                    print("OK: cleared ground.")
                elif args[:2] == ["item", "list"]:
                    names = [it.name for it in w.items_on_ground(p.year, p.x, p.y)]
                    print(f"[dev] ground: {names}")
                elif args[:2] == ["mon", "count"]:
                    print(w.monster_count(p.year))
                elif args[:2] == ["mon", "here"]:
                    if w.has_monster(p.year, p.x, p.y):
                        w.remove_monster(p.year, p.x, p.y)
                        print("Removed monster.")
                    else:
                        w.place_monster(p.year, p.x, p.y, "mutant")
                        print("Spawned monster.")
                elif (
                    args[:2] == ["mon", "spawn"]
                    and len(args) >= 3
                    and args[2].isdigit()
                ):
                    import random

                    n = int(args[2])
                    radius = 4
                    coords = []
                    grid = w.year(p.year).grid
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            nx, ny = p.x + dx, p.y + dy
                            if not grid.is_walkable(nx, ny):
                                continue
                            if w.has_monster(p.year, nx, ny):
                                continue
                            coords.append((nx, ny))
                    rng = random.Random(
                        hash((save.global_seed, p.year, p.x, p.y, "spawn_near"))
                    )
                    rng.shuffle(coords)
                    placed = 0
                    for x, y in coords:
                        w.place_monster(p.year, x, y, "mutant")
                        placed += 1
                        if placed >= n:
                            break
                    print(f"Spawned {placed} monster(s).")
                elif args and args[0] == "shadow" and len(args) == 2:
                    direction = args[1]
                    if direction in {"north", "south", "east", "west"}:
                        p.senses.add_shadow(cast(Direction, direction))
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
                elif args and args[0] == "today" and len(args) >= 2:
                    if args[1].lower() == "clear":
                        save.fake_today_override = None
                        print("OK.")
                    else:
                        try:
                            datetime.date.fromisoformat(args[1])
                            save.fake_today_override = args[1]
                            print("OK.")
                        except Exception:
                            print("Use YYYY-MM-DD.")
                elif args and args[0] == "topup":
                    count = daily_topup_if_needed(w, p, save)
                    print(f"Topped up {count} item(s).")
                else:
                    print("Invalid debug command.")
        elif cmd in {"north", "south", "east", "west"}:
            moved = p.move(cmd, w)
            if moved:
                last_move = cmd
            if p._last_move_struck_back:
                context._suppress_room_render = True
            if moved or p._last_move_struck_back:
                turn = True
            context._needs_render = True
        elif cmd == "travel":
            ok = handle_travel(args)
            if ok:
                turn = True
                context._needs_render = True
        elif cmd == "exit":
            macro_store.save_profile(p.clazz or "default")
            w.reset_all_aggro()
            print("Goodbye.")
            context.running = False
        else:
            print("Unknown command.")
            return False
        context._last_turn_consumed = turn
        persistence.save(p, w, save)
        return True

    def dispatch_macro(cmd_raw: str) -> bool:
        context._last_turn_consumed = False
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
            if len(parts) > 1:
                render_help_hint()
            else:
                print(SEP)
                print(f"You're {gerundize(head)}!")
            return False
        if cmd == "macro":
            handle_macro(tail)
            return True
        args = tail.split()
        return handle_command(cmd, args)

    def dispatch_line(line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            context._last_turn_consumed = False
            render_help_hint()
            return False
        print(stripped)
        before = (p.year, p.x, p.y)
        dispatch_macro(line)
        if not context.running:
            return True
        moved = (p.year, p.x, p.y) != before
        if moved:
            yells = w.on_entry_aggro_check(
                p.year, p.x, p.y, p, seed_parts=(save.global_seed, w.turn)
            )
            context._entry_yells = yells
        if context._needs_render:
            context._pre_shadow_lines = render_mod.shadow_lines(w, p)
        consumed = context._last_turn_consumed
        if consumed:
            if w.any_aggro_in_year(p.year):
                arrivals, foot = w.move_monsters_one_tick(p.year, p)
                context._arrivals_this_tick = arrivals
                context._footsteps_event = foot
            else:
                context._arrivals_this_tick = []
                context._footsteps_event = None
            w.turn += 1
        if context._needs_render and not context._suppress_room_render:
            render_room_view(p, w, context, include_arrivals=False)
            context._needs_render = False
        elif context._suppress_room_render:
            context._needs_render = False
            context._suppress_room_render = False
        for msg in render_mod.entry_yell_lines(context):
            print(msg)
        arrivals = render_mod.arrival_lines(context)
        if arrivals:
            print(SEP)
            for i, msg in enumerate(arrivals):
                print(red(msg))
                if i < len(arrivals) - 1:
                    print(SEP)
        for msg in render_mod.footsteps_lines(context):
            print(msg)
        return False

    context.run_script = lambda script: macro_store.expand_and_run_script(
        script, dispatch_macro
    )
    context.dispatch_line = dispatch_line
    context.try_dispatch_builtin = dispatch_macro

    return context
