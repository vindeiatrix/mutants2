from .theme import yellow, red, SEP
import re

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def enumerate_duplicates(items: list[str]) -> list[str]:
    """Return ``items`` with duplicate names enumerated sequentially."""
    seen: dict[str, int] = {}
    out: list[str] = []
    for name in items:
        idx = seen.get(name, 0)
        out.append(name if idx == 0 else f"{name} ({idx})")
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

    disp = CLASS_DISPLAY.get(class_key(p.clazz or ""), p.clazz or "")
    lines = [
        yellow(f"Name: Vindeiatrix / Mutant {disp}"),
        yellow("Exhaustion   : 0"),
        yellow(
            f"Str: {p.strength:<2}   Int: {p.intelligence:<2}   Wis: {p.wisdom:<2}"
        ),
        yellow(
            f"Dex: {p.dexterity:<2}   Con: {p.constitution:<2}   Cha: {p.charisma:<2}"
        ),
        yellow(f"Hit Points   : {p.hp} / {p.max_hp}"),
        yellow(f"Exp. Points  : {p.exp}           Level: {p.level}"),
        yellow(f"Riblets      : {getattr(p, 'riblets', 0)}"),
        yellow(f"Ions         : {p.ions}"),
        yellow(f"Wearing Armor: Nothing.  Armour Class: {p.ac_total}"),
        yellow("Ready to Combat: NO ONE"),
        yellow("Readied Spell : No spell memorized."),
        yellow(f"Year A.D.     : {p.year}"),
        "",
    ]
    return lines


def render_kill_block(name: str, xp: int, riblets: int, ions: int) -> None:
    """Render the red kill message block for monster deaths."""
    print(red(f"You have slain {name}!"))
    print(red(f"Your experience points are increased by {xp}!"))
    print(red(f"You collect {riblets} Riblets and {ions} ions from the slain body."))
    print("***")
