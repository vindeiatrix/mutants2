import re

_VOWEL_SOUND_INITIALS = tuple("AEIOUaeiou")
_AN_LETTERLIKE = set("FHLMNRSX")  # Letters pronounced with initial vowel sound


def article_for(name: str) -> str:
    """
    Return 'An' or 'A' for a given display name by approximate pronunciation.
    Rules:
      - True vowels → 'An' (Ion-Pack → An)
      - Leading digits that start with a vowel sound: 8/11/18
      - Single-letter or ALL-CAPS acronyms starting with F/H/L/M/N/R/S/X → 'An'
      - Otherwise → 'A'
    """
    s = name.strip()
    if not s:
        return "A"
    first = s[0]
    if first in _VOWEL_SOUND_INITIALS:
        return "An"
    if len(s) == 1 and s.isalpha() and s.upper() in _AN_LETTERLIKE:
        return "An"
    if re.match(r"^[A-Z]{2,}", s) and s[0] in _AN_LETTERLIKE:
        return "An"
    if re.match(r"^(8|11|18)\b", s):
        return "An"
    return "A"
