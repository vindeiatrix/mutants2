from typing import Optional

# Canonical internal ids (stable): use lowercase strings
CANON = {
    # arrows / navigation
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "home": "home",
    "end": "end",
    "pageup": "pageup",
    "pagedown": "pagedown",
    # function keys
    **{f"f{i}": f"f{i}" for i in range(1, 13)},
    # specials
    "tab": "tab",
    "enter": "enter",
    "escape": "escape",
    "space": "space",
}

# Keypad aliases → preferred canonical id; fallback char where applicable
KEYPAD = {
    "kp0": ("kp0", "0"),
    "kp1": ("kp1", "1"),
    "kp2": ("kp2", "2"),
    "kp3": ("kp3", "3"),
    "kp4": ("kp4", "4"),
    "kp5": ("kp5", "5"),
    "kp6": ("kp6", "6"),
    "kp7": ("kp7", "7"),
    "kp8": ("kp8", "8"),
    "kp9": ("kp9", "9"),
    "kp_plus": ("kp_plus", "+"),
    "kp_minus": ("kp_minus", "-"),
    "kp_mul": ("kp_mul", "*"),
    "kp_div": ("kp_div", "/"),
    "kp_enter": ("kp_enter", "enter"),
    "kp_dot": ("kp_dot", "."),
}


def normalize_key(name: str) -> Optional[str]:
    """Return canonical form for *name* or ``None`` if unknown."""
    n = name.strip().lower()
    if n in CANON:
        return n
    if len(n) == 1:
        return n
    if n in KEYPAD:
        return n
    if n.startswith("f") and n[1:].isdigit():
        i = int(n[1:])
        if 1 <= i <= 12:
            return f"f{i}"
    return None


def keypad_fallback(key: str) -> Optional[str]:
    """Return fallback char/canonical id for a keypad *key* or ``None``."""
    if key in KEYPAD:
        return KEYPAD[key][1]
    return None
