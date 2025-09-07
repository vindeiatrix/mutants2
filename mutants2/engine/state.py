from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple, TYPE_CHECKING

from .types import ItemInstance
from .items_util import coerce_item


if TYPE_CHECKING:  # pragma: no cover - import cycle guard
    from .player import Player


def allowed_centuries() -> list[int]:
    from .world import ALLOWED_CENTURIES

    return ALLOWED_CENTURIES


@dataclass
class CharacterProfile:
    year: int = field(default_factory=lambda: allowed_centuries()[0])
    positions: Dict[int, Tuple[int, int]] = field(
        default_factory=lambda: {c: (0, 0) for c in allowed_centuries()}
    )
    inventory: list[ItemInstance] = field(default_factory=list)
    hp: int = 10
    max_hp: int = 10
    ions: int = 0
    riblets: int = 0
    level: int = 1
    exp: int = 0
    strength: int = 0
    intelligence: int = 0
    wisdom: int = 0
    dexterity: int = 0
    constitution: int = 0
    charisma: int = 0
    ac: int = 0
    natural_dex_ac: int = 0
    ac_total: int = 0
    ready_to_combat_id: str | None = None
    ready_to_combat_name: str | None = None
    worn_armor: ItemInstance | str | None = None
    wielded_weapon: ItemInstance | str | None = None
    macros_name: str | None = None
    tables_migrated: bool = True


def profile_from_player(p: "Player") -> CharacterProfile:
    """Extract a :class:`CharacterProfile` from ``p``."""

    return CharacterProfile(
        year=p.year,
        positions=dict(p.positions),
        inventory=list(p.inventory),
        hp=p.hp,
        max_hp=p.max_hp,
        ions=p.ions,
        riblets=getattr(p, "riblets", 0),
        level=getattr(p, "level", 1),
        exp=getattr(p, "exp", 0),
        strength=getattr(p, "strength", 0),
        intelligence=getattr(p, "intelligence", 0),
        wisdom=getattr(p, "wisdom", 0),
        dexterity=getattr(p, "dexterity", 0),
        constitution=getattr(p, "constitution", 0),
        charisma=getattr(p, "charisma", 0),
        ac=getattr(p, "ac", 0),
        natural_dex_ac=getattr(p, "natural_dex_ac", 0),
        ac_total=getattr(p, "ac_total", getattr(p, "ac", 0)),
        ready_to_combat_id=getattr(p, "ready_to_combat_id", None),
        ready_to_combat_name=getattr(p, "ready_to_combat_name", None),
        worn_armor=getattr(p, "worn_armor", None),
        wielded_weapon=getattr(p, "wielded_weapon", None),
        tables_migrated=True,
    )


def apply_profile(p: "Player", prof: CharacterProfile) -> None:
    """Apply ``prof`` to ``p`` in-place."""

    p.year = prof.year
    p.positions = {int(y): (x, y2) for y, (x, y2) in prof.positions.items()}
    p.inventory = list(prof.inventory)
    p.hp = prof.hp
    p.max_hp = prof.max_hp
    p.ions = prof.ions
    p.riblets = getattr(prof, "riblets", 0)
    p.level = getattr(prof, "level", 1)
    p.exp = getattr(prof, "exp", 0)
    p.strength = getattr(prof, "strength", 0)
    p.intelligence = getattr(prof, "intelligence", 0)
    p.wisdom = getattr(prof, "wisdom", 0)
    p.dexterity = getattr(prof, "dexterity", 0)
    p.constitution = getattr(prof, "constitution", 0)
    p.charisma = getattr(prof, "charisma", 0)
    p.ac = getattr(prof, "ac", 0)
    p.natural_dex_ac = getattr(prof, "natural_dex_ac", p.dexterity // 10)
    p.ac_total = getattr(prof, "ac_total", p.ac + p.natural_dex_ac)
    p.ready_to_combat_id = getattr(prof, "ready_to_combat_id", None)
    p.ready_to_combat_name = getattr(prof, "ready_to_combat_name", None)
    p.worn_armor = getattr(prof, "worn_armor", None)
    p.wielded_weapon = getattr(prof, "wielded_weapon", None)
    p.recompute_ac()


def profile_to_raw(prof: CharacterProfile) -> dict:
    return {
        "year": prof.year,
        "positions": {
            str(y): {"x": x, "y": yy} for y, (x, yy) in prof.positions.items()
        },
        "inventory": [dict(coerce_item(i)) for i in prof.inventory],
        "hp": prof.hp,
        "max_hp": prof.max_hp,
        "ions": prof.ions,
        "riblets": getattr(prof, "riblets", 0),
        "level": getattr(prof, "level", 1),
        "exp": getattr(prof, "exp", 0),
        "strength": getattr(prof, "strength", 0),
        "intelligence": getattr(prof, "intelligence", 0),
        "wisdom": getattr(prof, "wisdom", 0),
        "dexterity": getattr(prof, "dexterity", 0),
        "constitution": getattr(prof, "constitution", 0),
        "charisma": getattr(prof, "charisma", 0),
        "ac": getattr(prof, "ac", 0),
        "natural_dex_ac": getattr(prof, "natural_dex_ac", 0),
        "ac_total": getattr(prof, "ac_total", getattr(prof, "ac", 0)),
        "ready_to_combat_id": getattr(prof, "ready_to_combat_id", None),
        "ready_to_combat_name": getattr(prof, "ready_to_combat_name", None),
        "worn_armor": (
            prof.worn_armor
            if isinstance(prof.worn_armor, str) or prof.worn_armor is None
            else dict(coerce_item(prof.worn_armor))
        ),
        "wielded_weapon": (
            prof.wielded_weapon
            if isinstance(prof.wielded_weapon, str) or prof.wielded_weapon is None
            else dict(coerce_item(prof.wielded_weapon))
        ),
        "tables_migrated": getattr(prof, "tables_migrated", True),
        **({"macros_name": prof.macros_name} if prof.macros_name else {}),
    }


def profile_from_raw(data: dict) -> CharacterProfile:
    inv_raw = data.get("inventory", [])
    if isinstance(inv_raw, list):
        inventory = [coerce_item(v) for v in inv_raw]
    else:
        inventory = [coerce_item(k) for k, v in inv_raw.items() for _ in range(int(v))]
    return CharacterProfile(
        year=int(data.get("year", allowed_centuries()[0])),
        positions={
            int(k): (v.get("x", 0), v.get("y", 0))
            for k, v in data.get("positions", {}).items()
        },
        inventory=inventory,
        hp=int(data.get("hp", 10)),
        max_hp=int(data.get("max_hp", 10)),
        ions=int(data.get("ions", 0)),
        riblets=int(data.get("riblets", 0)),
        level=int(data.get("level", 1)),
        exp=int(data.get("exp", 0)),
        strength=int(data.get("strength", 0)),
        intelligence=int(data.get("intelligence", 0)),
        wisdom=int(data.get("wisdom", 0)),
        dexterity=int(data.get("dexterity", 0)),
        constitution=int(data.get("constitution", 0)),
        charisma=int(data.get("charisma", 0)),
        ac=int(data.get("ac", 0)),
        natural_dex_ac=int(data.get("natural_dex_ac", 0)),
        ac_total=int(data.get("ac_total", int(data.get("ac", 0)))),
        ready_to_combat_id=data.get("ready_to_combat_id"),
        ready_to_combat_name=data.get("ready_to_combat_name"),
        worn_armor=(
            coerce_item(data["worn_armor"])
            if data.get("worn_armor") is not None
            else None
        ),
        wielded_weapon=(
            coerce_item(data["wielded_weapon"])
            if data.get("wielded_weapon") is not None
            else None
        ),
        macros_name=data.get("macros_name"),
        tables_migrated=bool(data.get("tables_migrated", False)),
    )
