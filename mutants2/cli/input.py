VOWELS = set("aeiou")


def gerundize(word: str) -> str:
    """Return a gerund form of ``word`` according to simple English rules."""
    w = word.strip()
    lower = w.lower()
    if lower.endswith("e") and not lower.endswith("ee"):
        return w[:-1] + "ing"
    if (
        len(lower) >= 3
        and lower[-1] not in VOWELS.union({"w", "x", "y"})
        and lower[-1].isalpha()
        and lower[-2] in VOWELS
        and lower[-3] not in VOWELS
    ):
        return w + w[-1] + "ing"
    return w + "ing"
