import re

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def visible_len(s: str) -> int:
    return len(ANSI.sub("", s))


def wrap_paragraph_ansi(text: str, width: int = 80) -> str:
    """
    Wrap a paragraph to 'width' visible columns:
    - no breaking words
    - no breaking on hyphens (treat hyphenated compounds as whole words)
    - preserves ANSI color codes
    """
    # Remove any hard line breaks coming in
    text = " ".join(text.split())

    # Tokenize on spaces but keep ANSI codes embedded in tokens.
    raw_tokens = text.split(" ")

    lines, cur = [], ""
    for tok in raw_tokens:
        # never split tokens; compute length if we were to add this token
        candidate = tok if not cur else f"{cur} {tok}"
        if visible_len(candidate) <= width:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            # if a single token is wider than width, place it alone (no hard splitting)
            cur = tok
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def wrap_list_ansi(
    items: list[str], width: int = 80, trailing_period: bool = True
) -> str:
    """
    Wrap a comma-separated list where each item is an unbreakable token
    (e.g., 'Cheese\u00a0(1)'); commas attach to the preceding token.
    """
    sep = " "
    lines, cur = [], ""
    for i, it in enumerate(items):
        token = it + ("," if i < len(items) - 1 else "")
        candidate = token if not cur else f"{cur}{sep}{token}"
        if visible_len(candidate) <= width:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = token
    if cur:
        if trailing_period and not cur.endswith("."):
            cur = cur + "."
        lines.append(cur)
    return "\n".join(lines)
