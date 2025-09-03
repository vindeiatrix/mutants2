from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from .senses import SensesBuffer
from . import items as items_mod


# Available player classes. These are simple placeholders for now and do not
# affect gameplay beyond being tracked and persisted.
CLASS_LIST = ["Warrior", "Mage", "Wizard", "Thief", "Priest"]
CLASS_BY_NUM = {str(i + 1): c for i, c in enumerate(CLASS_LIST)}
CLASS_BY_NAME = {c.lower(): c for c in CLASS_LIST}


@dataclass
class Player:
    """Player state including position for each year."""

    year: int = 2000
    positions: Dict[int, Tuple[int, int]] = field(
        default_factory=lambda: {2000: (0, 0), 2100: (0, 0)}
    )
    clazz: str | None = None
    senses: SensesBuffer = field(default_factory=SensesBuffer, repr=False)
    inventory: Dict[str, int] = field(default_factory=dict)
    hp: int = 10
    max_hp: int = 10

    @property
    def x(self) -> int:
        return self.positions[self.year][0]

    @property
    def y(self) -> int:
        return self.positions[self.year][1]

    def move(self, direction: str, world) -> bool:
        x, y = self.positions.setdefault(self.year, (0, 0))
        if direction not in {"north", "south", "east", "west"}:
            print("can't go that way.")
            return False
        if world.is_open(self.year, x, y, direction):
            nx, ny = world.step(x, y, direction)
            self.positions[self.year] = (nx, ny)
            return True
        print("can't go that way.")
        return False

    def travel(self, world, target_year: int | None = None) -> None:
        """Travel to ``target_year`` resetting position to origin."""
        if target_year is None:
            self.year = 2100 if self.year == 2000 else 2000
        else:
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

