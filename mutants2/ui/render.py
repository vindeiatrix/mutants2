from .theme import SEP, COLOR_HEADER, COLOR_ITEM
from .strings import (
    help_text,
    kill_reward,
)
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


def render_single_exit(direction: str, desc: str) -> str:
    pad = max(0, 5 - len(direction))
    return f"{COLOR_HEADER(direction)}{' ' * pad} – {COLOR_ITEM(desc)}"


def render_help_hint() -> None:
    """Print the standard help hint."""
    print(SEP)
    print(help_text("Type ? if you need assistance."))


def print_yell(mon) -> str:
    """Return the yell line for a monster."""
    name = mon.get("name") or mon.get("key")
    return f"{name} yells at you!"


def render_status(p) -> list[str]:
    from ..engine.player import CLASS_DISPLAY, class_key  # local import to avoid cycle
    from ..engine.items_resolver import get_item_def_by_key
    from ..engine.items_util import coerce_item
    from .items_render import display_item_name_plain

    disp = CLASS_DISPLAY.get(class_key(p.clazz or ""), p.clazz or "")
    armor_name = "Nothing."
    if getattr(p, "worn_armor", None):
        inst = coerce_item(p.worn_armor)
        idef = get_item_def_by_key(inst["key"])
        armor_name = display_item_name_plain(inst, idef)
    lines = [
        f"{COLOR_ITEM('Name:')} Vindeiatrix / Mutant {disp}",
        f"{COLOR_ITEM('Exhaustion   :')} 0",
        (
            f"{COLOR_ITEM('Str:')} {fmt(p.strength):<2}   "
            f"{COLOR_ITEM('Int:')} {fmt(p.intelligence):<2}   "
            f"{COLOR_ITEM('Wis:')} {fmt(p.wisdom):<2}"
        ),
        (
            f"{COLOR_ITEM('Dex:')} {fmt(p.dexterity):<2}   "
            f"{COLOR_ITEM('Con:')} {fmt(p.constitution):<2}   "
            f"{COLOR_ITEM('Cha:')} {fmt(p.charisma):<2}"
        ),
        f"{COLOR_ITEM('Hit Points   :')} {fmt(p.hp)} / {fmt(p.max_hp)}",
        f"{COLOR_ITEM('Exp. Points  :')} {fmt(p.exp)}           {COLOR_ITEM('Level:')} {fmt(p.level)}",
        f"{COLOR_ITEM('Riblets      :')} {fmt(getattr(p, 'riblets', 0))}",
        f"{COLOR_ITEM('Ions         :')} {fmt(p.ions)}",
        (
            f"{COLOR_ITEM('Wearing Armor:')} {armor_name}  "
            f"{COLOR_ITEM('Armour Class:')} {fmt(p.ac_total)}"
        ),
        (
            f"{COLOR_ITEM('Ready to Combat:')} {p.ready_to_combat_name}"
            if p.ready_to_combat_name
            else f"{COLOR_ITEM('Ready to Combat:')} NO ONE"
        ),
        f"{COLOR_ITEM('Readied Spell :')} No spell memorized.",
        f"{COLOR_ITEM('Year A.D.     :')} {fmt(p.year)}",
        "",
    ]
    return lines


def render_kill_block(riblets: int, ions: int) -> None:
    """Render the loot collection line for monster deaths."""
    print(
        kill_reward(
            f"You collect {fmt(riblets)} Riblets and {fmt(ions)} ions from the slain body."
        )
    )
