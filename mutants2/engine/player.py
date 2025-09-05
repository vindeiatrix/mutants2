from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple, cast

from .senses import SensesBuffer
from .types import Direction
from . import items as items_mod
from .world import ALLOWED_CENTURIES
from ..ui.theme import red


def class_key(name: str) -> str:
    """Return the canonical key for ``name``."""

    return name.strip().lower()


# Available player classes. These are simple placeholders for now and do not
# affect gameplay beyond being tracked and persisted.  The order here controls
# the class selection menu ordering.
CLASS_LIST = ["Thief", "Priest", "Wizard", "Warrior", "Mage"]
CLASS_DISPLAY = {class_key(c): c for c in CLASS_LIST}
CLASS_BY_NUM = {str(i + 1): class_key(c) for i, c in enumerate(CLASS_LIST)}
CLASS_BY_NAME = {class_key(c): class_key(c) for c in CLASS_LIST}


@dataclass
class Player:
    """Player state including position for each year."""

    year: int = ALLOWED_CENTURIES[0]
    positions: Dict[int, Tuple[int, int]] = field(
        default_factory=lambda: {c: (0, 0) for c in ALLOWED_CENTURIES}
    )
    clazz: str | None = None
    senses: SensesBuffer = field(default_factory=SensesBuffer, repr=False)
    inventory: Dict[str, int] = field(default_factory=dict)
    hp: int = 10
    max_hp: int = 10
    ions: int = 0
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
    _last_move_struck_back: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        if self.clazz and self.strength == 0 and self.max_hp == 10 and self.hp == 10:
            from . import classes as classes_mod

            classes_mod.apply_class_defaults(self, class_key(self.clazz))
        self.recompute_ac()

    def recompute_ac(self) -> None:
        """Recompute natural and total armour class."""
        self.natural_dex_ac = self.dexterity // 10
        self.ac_total = self.ac + self.natural_dex_ac

    @property
    def x(self) -> int:
        return self.positions[self.year][0]

    @property
    def y(self) -> int:
        return self.positions[self.year][1]

    def move(self, direction: str, world) -> bool:
        x, y = self.positions.setdefault(self.year, (0, 0))
        self._last_move_struck_back = False
        if direction not in {"north", "south", "east", "west"}:
            print("can't go that way.")
            return False
        d = cast(Direction, direction)
        if world.is_open(self.year, x, y, d):
            nx, ny = world.step(x, y, d)
            self.positions[self.year] = (nx, ny)
            return True
        self._last_move_struck_back = True
        print(red("You are struck back."))
        return False

    def travel(self, world, target_year: int) -> None:
        """Travel to ``target_year`` resetting position to origin."""
        self.year = target_year
        world.year(self.year)  # ensure world generation
        self.positions[self.year] = (0, 0)

    # Combat helpers ---------------------------------------------------------

    def heal_full(self) -> None:
        self.hp = self.max_hp

    def take_damage(self, dmg: int) -> None:
        self.hp = max(0, self.hp - max(0, dmg))

    def is_dead(self) -> bool:
        return self.hp <= 0

    # Inventory helpers ------------------------------------------------------

    def inventory_names_in_order(self) -> list[str]:
        """Return inventory item names preserving insertion order."""
        return [items_mod.REGISTRY[k].name for k in self.inventory.keys()]

    def inventory_weight_lbs(self) -> int:
        total = 0
        for key, count in self.inventory.items():
            item = items_mod.REGISTRY.get(key)
            if item and item.weight_lbs:
                total += item.weight_lbs * count
        return total

    def pick_up(self, name: str, world) -> None:
        """Pick up an item by name from the ground at the current tile."""
        item = items_mod.find_by_name(name)
        if not item:
            return
        ok = world.remove_ground_item(self.year, self.x, self.y, item.key)
        if ok:
            self.inventory[item.key] = self.inventory.get(item.key, 0) + 1

    def drop_to_ground(self, name: str, world) -> tuple[bool, str | None]:
        """Drop an item by name onto the ground at the current tile."""
        item = items_mod.find_by_name(name)
        if not item:
            return False, None
        if self.inventory.get(item.key, 0) <= 0:
            return False, "You don't have that."
        world.add_ground_item(self.year, self.x, self.y, item.key)
        self.inventory[item.key] -= 1
        if self.inventory[item.key] == 0:
            del self.inventory[item.key]
        return True, None

    def convert_item(self, name: str) -> items_mod.ItemDef | None:
        """Convert an inventory item to ions.

        Returns the :class:`ItemDef` of the item converted, or ``None`` if the
        item was not present or could not be converted.
        """
        item = items_mod.find_by_name(name)
        if not item:
            return None
        if self.inventory.get(item.key, 0) <= 0:
            return None
        if item.ion_value is None:
            return None
        self.inventory[item.key] -= 1
        if self.inventory[item.key] == 0:
            del self.inventory[item.key]
        self.ions += item.ion_value
        return item
