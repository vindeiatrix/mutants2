import re


def norm_name(s: str) -> str:
    """Normalize a name by lowercasing and stripping non-alphanumerics."""
    return re.sub(r"[^a-z0-9]", "", s.lower())
