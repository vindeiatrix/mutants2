from .theme import yellow, red, SEP
import re

NBSP = "\u00a0"  # non-breaking space

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def fmt(n: int) -> str:
    return str(int(n))


def enumerate_duplicates(items: list[str]) -> list[str]:
    """Return ``items`` with duplicate names enumerated sequentially."""
    seen: dict[str, int] = {}
    out: list[str] = []
    for name in items:
        idx = seen.get(name, 0)
        out.append(name if idx == 0 else f"{name}{NBSP}({idx})")
        seen[name] = idx + 1
    return out


def wrap_ansi(text: str, width: int = 80) -> str:
    """Wrap ``text`` at ``width`` visible characters, preserving ANSI codes."""
    tokens = text.split(" ")
    lengths = [len(ANSI_RE.sub("", tok)) for tok in tokens]
    lines: list[list[str]] = [[]]
    cur_len = 0
    for tok, length in zip(tokens, lengths):
        add = length if cur_len == 0 else length + 1
        if cur_len + add > width and lines[-1]:
            lines.append([tok])
            cur_len = length
        else:
            if cur_len:
                cur_len += 1 + length
            else:
                cur_len = length
            lines[-1].append(tok)
    return "\n".join(" ".join(line) for line in lines if line)


def render_help_hint() -> None:
    """Print the standard help hint in yellow."""
    print(SEP)
    print(yellow("Type ? if you need assistance."))


def print_yell(mon) -> str:
    """Return the yell line for a monster."""
    name = mon.get("name") or mon.get("key")
    return f"{name} yells at you!"


def render_status(p) -> list[str]:
    from ..engine.player import CLASS_DISPLAY, class_key  # local import to avoid cycle
    from ..engine import items as items_mod
    from ..engine.items_resolver import get_item_def_by_key
    from ..engine.items_util import coerce_item
    from .items_render import display_item_name

    disp = CLASS_DISPLAY.get(class_key(p.clazz or ""), p.clazz or "")
    armor_name = "Nothing."
    if getattr(p, "worn_armor", None):
        inst = coerce_item(p.worn_armor)
        idef = get_item_def_by_key(inst["key"])
        armor_name = display_item_name(inst, idef)
    lines = [
        yellow(f"Name: Vindeiatrix / Mutant {disp}"),
        yellow("Exhaustion   : 0"),
        yellow(
            f"Str: {fmt(p.strength):<2}   Int: {fmt(p.intelligence):<2}   Wis: {fmt(p.wisdom):<2}"
        ),
        yellow(
            f"Dex: {fmt(p.dexterity):<2}   Con: {fmt(p.constitution):<2}   Cha: {fmt(p.charisma):<2}"
        ),
        yellow(f"Hit Points   : {fmt(p.hp)} / {fmt(p.max_hp)}"),
        yellow(
            f"Exp. Points  : {fmt(p.exp)}           Level: {fmt(p.level)}"
        ),
        yellow(f"Riblets      : {fmt(getattr(p, 'riblets', 0))}"),
        yellow(f"Ions         : {fmt(p.ions)}"),
        yellow(
            f"Wearing Armor: {armor_name}  Armour Class: {fmt(p.ac_total)}"
        ),
        yellow(
            f"Ready to Combat: {p.ready_to_combat_name}" if p.ready_to_combat_name else "Ready to Combat: NO ONE"
        ),
        yellow("Readied Spell : No spell memorized."),
        yellow(f"Year A.D.     : {fmt(p.year)}"),
        "",
    ]
    return lines


def render_kill_block(name: str, xp: int, riblets: int, ions: int) -> None:
    """Render the red kill message block for monster deaths."""
    print(red(f"You have slain {name}!"))
    print(red(f"Your experience points are increased by {fmt(xp)}!"))
    print(red(f"You collect {fmt(riblets)} Riblets and {fmt(ions)} ions from the slain body."))
    print("***")
