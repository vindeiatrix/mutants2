from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from .world import ALLOWED_CENTURIES


@dataclass
class CharacterProfile:
    year: int = ALLOWED_CENTURIES[0]
    positions: Dict[int, Tuple[int, int]] = field(
        default_factory=lambda: {c: (0, 0) for c in ALLOWED_CENTURIES}
    )
    inventory: Dict[str, int] = field(default_factory=dict)
    hp: int = 10
    max_hp: int = 10
    ions: int = 0
