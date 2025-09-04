from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple, TYPE_CHECKING

from .world import ALLOWED_CENTURIES

if TYPE_CHECKING:  # pragma: no cover - import cycle guard
    from .player import Player


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
    macros_name: str | None = None


def profile_from_player(p: "Player") -> CharacterProfile:
    """Extract a :class:`CharacterProfile` from ``p``."""

    return CharacterProfile(
        year=p.year,
        positions=dict(p.positions),
        inventory=dict(p.inventory),
        hp=p.hp,
        max_hp=p.max_hp,
        ions=p.ions,
    )


def apply_profile(p: "Player", prof: CharacterProfile) -> None:
    """Apply ``prof`` to ``p`` in-place."""

    p.year = prof.year
    p.positions = {int(y): (x, y2) for y, (x, y2) in prof.positions.items()}
    p.inventory = dict(prof.inventory)
    p.hp = prof.hp
    p.max_hp = prof.max_hp
    p.ions = prof.ions


def profile_to_raw(prof: CharacterProfile) -> dict:
    return {
        "year": prof.year,
        "positions": {str(y): {"x": x, "y": yy} for y, (x, yy) in prof.positions.items()},
        "inventory": {k: v for k, v in prof.inventory.items()},
        "hp": prof.hp,
        "max_hp": prof.max_hp,
        "ions": prof.ions,
        **({"macros_name": prof.macros_name} if prof.macros_name else {}),
    }


def profile_from_raw(data: dict) -> CharacterProfile:
    return CharacterProfile(
        year=int(data.get("year", ALLOWED_CENTURIES[0])),
        positions={
            int(k): (v.get("x", 0), v.get("y", 0))
            for k, v in data.get("positions", {}).items()
        },
        inventory={k: int(v) for k, v in data.get("inventory", {}).items()},
        hp=int(data.get("hp", 10)),
        max_hp=int(data.get("max_hp", 10)),
        ions=int(data.get("ions", 0)),
        macros_name=data.get("macros_name"),
    )
