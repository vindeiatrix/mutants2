from .theme import yellow, SEP


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
        yellow("Riblets      : 0"),
        yellow(f"Ions         : {p.ions}"),
        yellow(f"Wearing Armor: Nothing.  Armour Class: {p.ac}"),
        yellow("Ready to Combat: NO ONE"),
        yellow("Readied Spell : No spell memorized."),
        yellow(f"Year A.D.     : {p.year}"),
        "",
    ]
    return lines
