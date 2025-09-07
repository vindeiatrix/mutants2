from __future__ import annotations

from types import SimpleNamespace
import datetime
import time
from typing import Mapping, MutableMapping, cast

from ..engine import persistence, items, monsters, combat
from ..engine.items_resolver import (
    resolve_key_prefix,
    get_item_def_by_key,
    resolve_key,
)
from ..ui.items_render import (
    display_item_name_plain,
    display_item_name_with_plus,
)
from ..engine.items_util import coerce_item
from ..engine.render import render_room_view
from ..engine import render as render_mod
from ..engine.loop import (
    maybe_process_upkeep,
    start_realtime_tick,
    stop_realtime_tick,
    TICK_SECONDS,
)
from ..engine.leveling import recompute_from_exp
from ..engine.player import (
    CLASS_LIST,
    CLASS_BY_NUM,
    CLASS_BY_NAME,
    class_key,
)
from ..engine.state import (
    CharacterProfile,
    apply_profile,
    profile_from_raw,
)
from mutants2.types import ItemInstance
from ..engine.gen import (
    daily_topup_if_needed,
    debug_item_topup,
    debug_monster_topup,
)
from ..engine.macros import MacroStore
from ..engine.types import Direction
from ..engine.world import ALLOWED_CENTURIES, LOWEST_CENTURY, HIGHEST_CENTURY
from ..ui.help import MACROS_HELP, ABBREVIATIONS_NOTE, COMMANDS_HELP, USAGE
from ..ui.strings import GET_WHAT, DROP_WHAT
from ..ui.theme import red, SEP, yellow, white
from ..data.config import ION_TRAVEL_COST, HEAL_K
from ..ui.render import (
    render_help_hint,
    render_status,
    enumerate_duplicates,
    fmt,
)
from ..ui.wrap import wrap_list_ansi
from .input import gerundize


_ION_SET_DEPRECATED_SHOWN = False


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
    "wear": "wear",
    "remove": "remove",
    "wield": "wield",
    "macro": "macro",
    "help": "help",
    "?": "help",
    "do": "do",
    "status": "status",
    "rest": "rest",
    "combat": "combat",
    "heal": "heal",
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
    "combat",
    "wear",
    "remove",
    "wield",
    "rest",
    "heal",
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


def ordinal(n: int) -> str:
    """Return the ordinal representation of ``n`` (1 -> ``1st``)."""

    if 10 <= (n % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def class_menu(p, w, save, context=None, *, in_game: bool) -> bool:
    """Show the class selection menu.

    Returns ``True`` if the player's class was changed, ``False`` otherwise.
    ``in_game`` distinguishes between startup and the ``class`` command.
    """
    print("Choose your class:")
    for i, name in enumerate(CLASS_LIST, 1):
        key = class_key(name)
        prof = save.profiles.get(key)
        if isinstance(prof, dict):
            prof = profile_from_raw(prof)
            save.profiles[key] = prof
        if isinstance(prof, CharacterProfile):
            level = getattr(prof, "level", 1)
            year = prof.year
            x, y = prof.positions.get(year, (0, 0))
        else:
            level = 1
            year = ALLOWED_CENTURIES[0]
            x, y = 0, 0
        print(
            f"{i:>2}. Mutant {name:<7}  Level: {level:>2}   Year: {year:<4}  ({x:>2}  {y:>2})"
        )
    if in_game and context is not None:
        context.in_game = False
    while True:
        try:
            s = input("class> ").strip().lower()
        except EOFError:
            s = ""
        if not s:
            continue
        if s in {"exit", "quit", "q"}:
            p.ready_to_combat_id = None
            p.ready_to_combat_name = None
            w.reset_all_aggro()
            persistence.save(p, w, save)
            print("Goodbye.")
            raise SystemExit
        if s == "?":
            print(COMMANDS_HELP)
            print()
            print(ABBREVIATIONS_NOTE)
            continue
        if s in {"back", "b"}:
            if in_game:
                if context is not None:
                    context.in_game = True
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
        k = class_key(picked)
        prof = save.profiles.get(k)
        if isinstance(prof, CharacterProfile):
            apply_profile(p, prof)
        elif isinstance(prof, dict):
            prof_obj = profile_from_raw(prof)
            save.profiles[k] = prof_obj
            apply_profile(p, prof_obj)
        else:
            apply_profile(p, CharacterProfile())
            from ..engine import classes as classes_mod

            classes_mod.apply_class_defaults(p, k)
        w.year(p.year)
        p.clazz = k
        persistence.save(p, w, save)
        if context is not None:
            context.in_game = True
        return True


def make_context(p, w, save, *, dev: bool = False):
    macro_store = MacroStore()
    macro_store.load_profile(class_key(p.clazz or "default"))
    last_move = None


    context = SimpleNamespace(
        macro_store=macro_store,
        running=True,
        player=p,
        world=w,
        save=save,
        tick_handle=None,
        in_game=True,
        _arrivals_this_tick=[],
        _footsteps_event=None,
        _entry_yells=[],
        _pre_shadow_lines=[],
        _needs_render=False,
        _last_turn_consumed=False,
        _suppress_room_render=False,
        _suppress_entry_aggro=False,
        _skip_movement_tick=False,
    )

    def request_render() -> None:
        context._needs_render = True

    context.request_render = request_render

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
        if year_input < LOWEST_CENTURY or year_input > HIGHEST_CENTURY:
            print(yellow("You can only travel from year 2000 to 3000!"))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        target = max(c for c in ALLOWED_CENTURIES if c <= year_input)
        if target == p.year:
            p.travel(w, target)
            ord_century = ordinal(target // 100)
            print(yellow(f"You're already in the {ord_century} Century!"))
        else:
            steps = abs(target - p.year) // 100
            cost = ION_TRAVEL_COST * steps
            if p.ions < cost:
                print(yellow("***"))
                print(yellow("You don't have enough ions to create a portal."))
            else:
                p.ions -= cost
                p.travel(w, target)
                print(
                    yellow(f"ZAAAAPPPPP!! You've been sent to the year {target} A.D.")
                )
        context._suppress_room_render = True
        context._suppress_entry_aggro = True
        context._skip_movement_tick = False
        context._needs_render = False
        return True

    def handle_get(args: list[str]) -> bool:
        if not args:
            print(GET_WHAT)
            return False
        raw = " ".join(args)
        ground_defs = {d.key: d for d in w.items_on_ground(p.year, p.x, p.y)}
        key = resolve_key_prefix(raw, ground_defs.keys())
        if not key:
            print(f'No item here matching "{raw}".')
            return False
        idef = ground_defs[key]
        overflow = p.pick_up(idef.name, w)
        if overflow:
            print(yellow("***"))
            print(yellow(f"The {overflow} fell out of your sack!"))
        print(f"You pick up {idef.name}.")
        return False

    def handle_drop(args: list[str]) -> bool:
        if not args:
            print(DROP_WHAT)
            return False
        raw = " ".join(args)
        inv_keys = [resolve_key(coerce_item(obj)["key"]) for obj in p.inventory]
        key = resolve_key_prefix(raw, inv_keys)
        if not key:
            print(f'No item in inventory matching "{raw}".')
            return False
        inst_match: ItemInstance | None = None
        for obj in p.inventory:
            inst = coerce_item(obj)
            if resolve_key(inst["key"]) == key:
                inst_match = inst
                break
        if inst_match is None:
            print(f'No item in inventory matching "{raw}".')
            return False
        idef = get_item_def_by_key(key)
        name = display_item_name_plain(inst_match, idef)
        ok, msg, sack_name, gift_name = p.drop_to_ground(idef.name if idef else key, w)
        print(f"You drop {name}." if ok else (msg or "You can’t drop that here."))
        if sack_name:
            print(yellow("***"))
            print(yellow(f"The {sack_name} fell out of your sack!"))
        if gift_name:
            print(yellow("***"))
            print(
                yellow(
                    f"{items.article_name(gift_name)} has magically appeared in your hand!"
                )
            )
        return False

    def handle_wear(args: list[str]) -> bool:
        if not args or args[0].lower() == "help":
            render_usage("wear")
            context._suppress_room_render = True
            return False
        raw = " ".join(args)
        inv_keys = [resolve_key(coerce_item(obj)["key"]) for obj in p.inventory]
        key = resolve_key_prefix(raw, inv_keys)
        if not key:
            print(yellow("***"))
            print(yellow(f"You're not carrying a {raw}."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        inst_match: ItemInstance | None = None
        for obj in p.inventory:
            inst = coerce_item(obj)
            if resolve_key(inst["key"]) == key:
                inst_match = inst
                break
        if inst_match is None:
            print(yellow("***"))
            print(yellow(f"You're not carrying a {raw}."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        idef = get_item_def_by_key(key)
        if not idef or idef.ac_bonus <= 0:
            print(yellow("***"))
            print(yellow("You can't wear that."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        print(yellow("***"))
        if p.worn_armor:
            old_inst = coerce_item(p.worn_armor)
            old_def = get_item_def_by_key(old_inst["key"])
            print(yellow(f"You remove the {display_item_name_plain(old_inst, old_def)}."))
        p.worn_armor = inst_match
        p.recompute_ac()
        print(yellow(f"You wear the {display_item_name_plain(inst_match, idef)}."))
        context._needs_render = False
        context._suppress_room_render = True
        return False

    def handle_remove(args: list[str]) -> bool:
        if args and args[0].lower() == "help":
            render_usage("remove")
            context._suppress_room_render = True
            return False
        if not p.worn_armor:
            print(yellow("***"))
            print(yellow("You're not wearing any armor."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        inst = coerce_item(p.worn_armor)
        idef = get_item_def_by_key(inst["key"])
        name = display_item_name_plain(inst, idef)
        p.worn_armor = None
        p.recompute_ac()
        print(yellow("***"))
        print(yellow(f"You remove the {name}."))
        context._needs_render = False
        context._suppress_room_render = True
        return False

    def handle_wield(args: list[str]) -> bool:
        if not args or args[0].lower() == "help":
            render_usage("wield")
            context._suppress_room_render = True
            return False
        raw = " ".join(args)
        inv_keys = [resolve_key(coerce_item(obj)["key"]) for obj in p.inventory]
        key = resolve_key_prefix(raw, inv_keys)
        if not key:
            print(yellow("***"))
            print(yellow(f"You're not carrying a {raw}."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        inst_match: ItemInstance | None = None
        for obj in p.inventory:
            inst = coerce_item(obj)
            if resolve_key(inst["key"]) == key:
                inst_match = inst
                break
        if inst_match is None:
            print(yellow("***"))
            print(yellow(f"You're not carrying a {raw}."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        idef = get_item_def_by_key(key)
        p.wielded_weapon = inst_match
        mon = w.monster_here(p.year, p.x, p.y)
        if not (
            p.ready_to_combat_id
            and mon
            and str(mon.get("id")) == p.ready_to_combat_id
        ):
            print(yellow("***"))
            print(yellow("You're not ready to combat anyone."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        print(yellow("***"))
        print(yellow(f"You wield the {display_item_name_plain(inst_match, idef)}."))
        key = inst_match["key"]
        dmg, killed, name_mon = combat.player_attack(p, w, key)
        print(yellow("***"))
        print(yellow(f"You hit {name_mon} for {dmg} damage.  (temp)"))
        context._needs_render = False
        context._suppress_room_render = True
        return False

    def handle_convert(args: list[str]) -> bool:
        if not args:
            render_usage("convert")
            context._suppress_room_render = True
            return False
        raw = " ".join(args)
        inv_keys = [resolve_key(coerce_item(inst)["key"]) for inst in p.inventory]
        key = resolve_key_prefix(raw, inv_keys)
        if not key:
            print(yellow("***"))
            print(yellow(f"You're not carrying a {raw}."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        key_match = None
        for inst in p.inventory:
            ci = coerce_item(inst)
            if resolve_key(ci["key"]) == key:
                key_match = ci
                break
        if key_match is None:
            print(yellow("***"))
            print(yellow(f"You're not carrying a {raw}."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        idef = get_item_def_by_key(key)
        item = p.convert_item(idef.name if idef else key)
        if not item:
            render_help_hint()
            return False
        print(SEP)
        print(yellow(f"The {item.name} vanishes with a flash!"))
        print(yellow(f"You convert the {item.name} into {fmt(item.ion_value)} ions."))
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
            return True

        raw = " ".join(args).strip()
        q = raw.lower()

        here_monsters = [
            monsters.REGISTRY[m["key"]].name for m in w.monsters_here(p.year, p.x, p.y)
        ]
        mname = monsters.first_mon_prefix(q, here_monsters)
        if mname:
            print(f"It's a {mname}.")
            return True

        ground_objs = w.ground.get((p.year, p.x, p.y), [])
        cand_keys = [resolve_key(coerce_item(obj)["key"]) for obj in p.inventory] + [
            resolve_key(coerce_item(obj)["key"]) for obj in ground_objs
        ]
        key = resolve_key_prefix(raw, cand_keys)
        inst_match: ItemInstance | None = None
        if key:
            for obj in p.inventory:
                inst = coerce_item(obj)
                if resolve_key(inst["key"]) == key:
                    inst_match = inst
                    break
            if inst_match is None:
                for obj in ground_objs:
                    inst = coerce_item(obj)
                    if resolve_key(inst["key"]) == key:
                        inst_match = inst
                        break
        if inst_match:
            print(yellow("***"))
            idef = get_item_def_by_key(inst_match["key"])
            lvl = inst_match.get("meta", {}).get("enchant_level")
            if lvl is None:
                lvl = inst_match.get("enchant") or 0
            base_name = display_item_name_plain(inst_match, idef)
            if lvl > 0:
                ench_name = display_item_name_with_plus(inst_match, idef)
                print(
                    yellow(
                        f"The {base_name} possesses a magical aura. "
                        f"Concentrating stronger, you realize this is a {ench_name}!"
                    )
                )
                return True
            desc = items.describe_instance(inst_match)
            if desc:
                print(desc)
                return True
            print(yellow(f"It looks like a lovely {base_name}!"))
            return True

        d = parse_dir_any_prefix(q)
        if d:
            if not w.is_open(p.year, p.x, p.y, d):
                print("You can't look that way.")
                return True
            ax, ay = w.step(p.x, p.y, d)
            text = render_mod.render_room_at(
                w,
                p.year,
                ax,
                ay,
                include_shadows=False,
            )
            print(text)
            return True

        print(yellow("***"))
        print(yellow(f"You're not carrying a {raw}."))
        context._needs_render = False
        context._suppress_room_render = True
        return False

    def handle_combat(args: list[str]) -> bool:
        if not args:
            render_usage("combat")
            context._suppress_room_render = True
            return False
        raw = " ".join(args).strip()
        here = w.monsters_here(p.year, p.x, p.y)
        names = [cast(str, m.get("name")) for m in here]
        match = monsters.first_mon_prefix(raw.lower(), names)
        if not match:
            print(yellow("***"))
            print(yellow("No such monster here."))
            context._needs_render = False
            context._suppress_room_render = True
            return False
        for m in here:
            if cast(str, m.get("name")) == match:
                p.ready_to_combat_id = str(m.get("id"))
                p.ready_to_combat_name = match
                break
        print(yellow("***"))
        print(yellow(f"You're ready to combat {match}!"))
        context._needs_render = False
        context._suppress_room_render = True
        return True

    def handle_rest() -> None:
        if w.monster_here(p.year, p.x, p.y):
            print("You can’t rest while a monster is here.")
            return
        p.heal_full()
        print(f"You rest and recover. (HP: {p.hp}/{p.max_hp})")

    def handle_heal() -> None:
        k = HEAL_K.get(class_key(p.clazz or ""), 0)
        heal_amount = p.level + 5
        cost = k * p.level
        if p.ions < cost:
            print(yellow("***"))
            print(yellow("You don't have enough ions to heal!"))
            return
        if p.hp >= p.max_hp:
            print(yellow("***"))
            print(yellow("Nothing happens!"))
            return
        p.ions -= cost
        p.hp = min(p.max_hp, p.hp + heal_amount)
        print(yellow("***"))
        print(yellow(f"Your body glows as it heals {heal_amount} points!"))
        if p.hp >= p.max_hp:
            print(yellow("***"))
            print(yellow("You're healed to the maximum!"))

    def handle_status() -> None:
        lines = render_status(p)
        total = fmt(p.inventory_weight_lbs())
        lines.append(
            yellow(
                f"You are carrying the following items:  (Total Weight: {total} LB's)"
            )
        )
        names = p.inventory_display_names()
        if names:
            labels = enumerate_duplicates(names)
            wrapped = wrap_list_ansi(labels)
            lines.extend(white(ln) for ln in wrapped.splitlines())
        else:
            lines.append("(empty)")
        for ln in lines:
            print(ln)

    def handle_command(cmd: str, args: list[str]) -> bool:
        nonlocal last_move
        turn = False
        if cmd == "look":
            turn = handle_look(args)
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
            macro_store.save_profile(class_key(p.clazz or "default"))
            persistence.save(p, w, save)
            stop_realtime_tick(context.tick_handle)
            context.tick_handle = None
            context.in_game = False
            w.reset_all_aggro()
            p.ready_to_combat_id = None
            p.ready_to_combat_name = None
            changed = class_menu(p, w, save, context, in_game=True)
            if changed:
                macro_store.load_profile(class_key(p.clazz or "default"))
                yells = w.on_entry_aggro_check(
                    p.year, p.x, p.y, p, seed_parts=(save.global_seed, w.turn)
                )
                render_room_view(p, w, context)
                for line in yells:
                    print(line)
            save.next_upkeep_tick = time.monotonic() + TICK_SECONDS
            context.tick_handle = start_realtime_tick(p, w, save, context)
            context.in_game = True
        elif cmd == "inventory":
            total = fmt(p.inventory_weight_lbs())
            print(
                yellow(
                    f"You are carrying the following items: (Total Weight: {total} LB's)"
                )
            )
            names = p.inventory_display_names()
            if names:
                labels = enumerate_duplicates(names)
                wrapped = wrap_list_ansi(labels)
                for ln in wrapped.splitlines():
                    print(white(ln))
            else:
                print("(empty)")
            context._needs_render = False
            context._suppress_room_render = True
        elif cmd == "get":
            handle_get(args)
            context._needs_render = False
            context._suppress_room_render = True
            turn = True
        elif cmd == "drop":
            handle_drop(args)
            turn = True
        elif cmd == "wear":
            handle_wear(args)
            turn = True
        elif cmd == "remove":
            handle_remove(args)
            turn = True
        elif cmd == "wield":
            handle_wield(args)
            turn = True
        elif cmd == "convert":
            if handle_convert(args):
                turn = True
        elif cmd == "combat":
            if handle_combat(args):
                turn = True
        elif cmd == "rest":
            handle_rest()
            turn = True
        elif cmd == "heal":
            handle_heal()
            turn = True
        elif cmd == "status":
            handle_status()
        elif cmd == "help":
            if args and args[0].lower() == "debug":
                print(
                    """Debug commands:
  debug set ion <N>                   Set ions to N.
  debug set exp <N>                   Set total experience points.
  debug set hp <N>                    Set current HP.
  debug set riblet <N>                Set riblets to N.
  debug item add <name|key> [count]   Add item(s) to current room's ground.
  debug item clear                    Remove all ground items here.
  debug item list                     Show raw ground items here.
  debug item count                    Count ground items in current year.
  debug item topup                    Run item top-up for current year.
  debug mon here                      Toggle a Mutant on this tile.
  debug mon clear                     Remove all monsters in this room.
  debug mon clear year                Remove all monsters in this year.
  debug mon spawn <n>                 Spawn n Mutants near the player (dev).
  debug mon count                     Count monsters in current year.
  debug mon topup                     Run monster top-up for current year.
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
                elif topic in USAGE:
                    for line in USAGE[topic]:
                        print(line)
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
                    extra = args[3:]
                    count = 1
                    enchant = None
                    if extra and extra[0].isdigit():
                        count = int(extra[0])
                        extra = extra[1:]
                    if extra and extra[0].startswith("+") and extra[0][1:].isdigit():
                        enchant = int(extra[0][1:])
                    key = resolve_key_prefix(name_or_key)
                    if not key:
                        print("Unknown item.")
                        return False
                    idef = get_item_def_by_key(key)
                    if not idef:
                        print("Unknown item.")
                        return False
                    for _ in range(count):
                        lvl = enchant
                        if lvl is None:
                            lvl = idef.default_enchant_level
                        inst = {"key": key}
                        if lvl:
                            inst["meta"] = {"enchant_level": lvl}
                        w.add_ground_item(p.year, p.x, p.y, inst)
                    print(f"OK: added {count} x {idef.name}.")
                elif args[:2] == ["item", "clear"]:
                    w.ground.pop((p.year, p.x, p.y), None)
                    print("OK: cleared ground.")
                elif args[:2] == ["item", "list"]:
                    names = [it.name for it in w.items_on_ground(p.year, p.x, p.y)]
                    print(f"[dev] ground: {names}")
                elif args[:2] == ["item", "count"]:
                    cnt = w.ground_items_count(p.year)
                    print(f"Items on ground in year {p.year}: {cnt}")
                elif args[:2] == ["item", "topup"]:
                    before, after, target = debug_item_topup(
                        w, p.year, save.global_seed
                    )
                    print(
                        f"Item top-up complete for {p.year}: {before} → {after} (target: {target})."
                    )
                elif args[:3] == ["mon", "clear", "year"]:
                    total = 0
                    coords = {(x, y) for x, y, _m in w.monster_positions(p.year)}
                    for x, y in coords:
                        while w.remove_monster(p.year, x, y):
                            total += 1
                    print(f"Cleared {total} monster(s) in year {p.year}.")
                elif args[:2] == ["mon", "clear"]:
                    n = 0
                    while w.remove_monster(p.year, p.x, p.y):
                        n += 1
                    print(f"Cleared {n} monster(s) in this room.")
                elif args[:2] == ["mon", "count"]:
                    w.year(p.year)
                    cnt = w.monster_count(p.year)
                    print(f"Monsters in year {p.year}: {cnt}")
                elif args[:2] == ["mon", "topup"]:
                    before, after, target = debug_monster_topup(
                        w, p.year, save.global_seed
                    )
                    print(
                        f"Monster top-up complete for {p.year}: {before} → {after} (target: {target})."
                    )
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
                elif args[:2] == ["set", "ion"] and len(args) >= 3:
                    try:
                        val = max(0, int(args[2]))
                    except ValueError:
                        print("Invalid ion value.")
                    else:
                        p.ions = val
                        print(yellow(f"Ions set to {val}."))
                elif (
                    args[:2] in (["set", "riblet"], ["set", "riblets"])
                    and len(args) >= 3
                ):
                    try:
                        val = max(0, int(args[2]))
                    except ValueError:
                        print("Invalid riblet value.")
                    else:
                        p.riblets = val
                        print(yellow(f"Riblets set to {val}."))
                elif args[:2] == ["ion", "set"] and len(args) >= 3:
                    global _ION_SET_DEPRECATED_SHOWN
                    if not _ION_SET_DEPRECATED_SHOWN:
                        print("debug ion set is deprecated; use debug set ion <N>.")
                        _ION_SET_DEPRECATED_SHOWN = True
                    try:
                        val = max(0, int(args[2]))
                    except ValueError:
                        print("Invalid ion value.")
                    else:
                        p.ions = val
                        print(yellow(f"Ions set to {val}."))
                elif args[:2] == ["set", "exp"] and len(args) >= 3:
                    try:
                        val = max(0, int(args[2]))
                    except ValueError:
                        print("Invalid EXP value.")
                    else:
                        p.exp = val
                        recompute_from_exp(p)
                        print(yellow(f"EXP set to {val}. Level is now {p.level}."))
                elif args[:2] == ["set", "hp"] and len(args) >= 3:
                    try:
                        val = int(args[2])
                    except ValueError:
                        print("Invalid HP value.")
                    else:
                        p.hp = max(0, min(val, p.max_hp))
                        print(yellow(f"HP set to {p.hp}/{p.max_hp}."))
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
            turn = handle_travel(args)
        elif cmd == "exit":
            macro_store.save_profile(class_key(p.clazz or "default"))
            p.ready_to_combat_id = None
            p.ready_to_combat_name = None
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
                print(yellow(f"You're {gerundize(head)}!"))
                print()
            context._last_turn_consumed = True
            return False
        if cmd == "macro":
            handle_macro(tail)
            return True
        args = tail.split()
        return handle_command(cmd, args)

    def dispatch_line(line: str) -> bool:
        maybe_process_upkeep(p, w, save, context)
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
            if context._suppress_entry_aggro:
                context._entry_yells = []
            else:
                yells = w.on_entry_aggro_check(
                    p.year, p.x, p.y, p, seed_parts=(save.global_seed, w.turn)
                )
                context._entry_yells = yells
        if context._needs_render:
            context._pre_shadow_lines = render_mod.shadow_lines(w, p)
        consumed = context._last_turn_consumed
        if consumed:
            if not context._skip_movement_tick and w.any_aggro_in_year(p.year):
                arrivals, foot = w.move_monsters_one_tick(p.year, p)
                context._arrivals_this_tick = arrivals
                context._footsteps_event = foot
            else:
                context._arrivals_this_tick = []
                context._footsteps_event = None
            w.turn += 1
            context._skip_movement_tick = False
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
        context._suppress_entry_aggro = False
        return False

    context.run_script = lambda script: macro_store.expand_and_run_script(
        script, dispatch_macro
    )
    context.dispatch_line = dispatch_line
    context.try_dispatch_builtin = dispatch_macro

    return context
