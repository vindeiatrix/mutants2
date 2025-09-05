from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple, cast

from .state import ItemInstance

from .senses import SensesBuffer
from .types import Direction
from . import items as items_mod, rng as rng_mod
from .world import ALLOWED_CENTURIES
from ..ui.theme import red


INVENTORY_LIMIT = 10
GROUND_LIMIT = 6


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
    inventory: list[ItemInstance | str] = field(default_factory=list)
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
        """Return inventory item names preserving pickup order."""
        names: list[str] = []
        for val in self.inventory:
            key = val.key if isinstance(val, ItemInstance) else val
            names.append(items_mod.REGISTRY[key].name)
        return names

    def inventory_weight_lbs(self) -> int:
        total = 0
        for val in self.inventory:
            key = val.key if isinstance(val, ItemInstance) else val
            item = items_mod.REGISTRY.get(key)
            if item and item.weight_lbs:
                total += item.weight_lbs
        return total

    def pick_up(self, name: str, world) -> str | None:
        """Pick up an item by name from the ground at the current tile."""
        item = items_mod.find_by_name(name)
        if not item:
            return None
        inst = world.remove_ground_item(self.year, self.x, self.y, item.key)
        if inst is None:
            return None
        self.inventory.append(inst)

        overflow_name: str | None = None
        total = len(self.inventory)
        if total > INVENTORY_LIMIT:
            rng = rng_mod.hrand(
                world.global_seed, world.turn, self.year, self.x, self.y, "inv_overflow"
            )
            candidates = [
                it for it in self.inventory if (it.key if isinstance(it, ItemInstance) else it) != item.key
            ]
            if candidates:
                victim = rng.choice(candidates)
                try:
                    self.inventory.remove(victim)
                except ValueError:
                    pass
                world.add_ground_item(self.year, self.x, self.y, victim)
                vkey = victim.key if isinstance(victim, ItemInstance) else victim
                overflow_name = items_mod.REGISTRY[vkey].name
        return overflow_name

    def drop_to_ground(
        self, name: str, world
    ) -> tuple[bool, str | None, str | None, str | None]:
        """Drop an item by name onto the ground at the current tile.

        Returns ``(ok, msg, sack_name, gift_name)`` where ``sack_name`` is the
        name of an item that fell out of the sack due to inventory overflow and
        ``gift_name`` is a ground item that was swapped into the inventory when
        the ground was over capacity.
        """

        item = items_mod.find_by_name(name)
        if not item:
            return False, None, None, None
        inv_obj = None
        for it in self.inventory:
            key = it.key if isinstance(it, ItemInstance) else it
            if key == item.key:
                inv_obj = it
                break
        if inv_obj is None:
            return False, "You don't have that.", None, None

        world.add_ground_item(self.year, self.x, self.y, inv_obj)
        self.inventory.remove(inv_obj)

        rng = rng_mod.hrand(
            world.global_seed, world.turn, self.year, self.x, self.y, "drop_overflow"
        )
        sack_name: str | None = None
        gift_name: str | None = None

        ground_items = world.items_on_ground(self.year, self.x, self.y)
        if len(ground_items) > GROUND_LIMIT:
            candidates = [it for it in ground_items if it.key != item.key]
            if candidates:
                gift_def = rng.choice(candidates)
                gift_inst = world.remove_ground_item(
                    self.year, self.x, self.y, gift_def.key
                )
                if gift_inst is not None:
                    self.inventory.append(gift_inst)
                    gift_name = gift_def.name

                    total = len(self.inventory)
                    if total > INVENTORY_LIMIT:
                        inv_candidates = [
                            it
                            for it in self.inventory
                            if (it.key if isinstance(it, ItemInstance) else it) != gift_def.key
                        ]
                        if inv_candidates:
                            victim = rng.choice(inv_candidates)
                            self.inventory.remove(victim)
                            world.add_ground_item(
                                self.year, self.x, self.y, victim
                            )
                            vkey = (
                                victim.key if isinstance(victim, ItemInstance) else victim
                            )
                            sack_name = items_mod.REGISTRY[vkey].name

        return True, None, sack_name, gift_name

    def convert_item(self, name: str) -> items_mod.ItemDef | None:
        """Convert an inventory item to ions.

        Returns the :class:`ItemDef` of the item converted, or ``None`` if the
        item was not present or could not be converted.
        """
        item = items_mod.find_by_name(name)
        if not item:
            return None
        inv_obj = None
        for it in self.inventory:
            key = it.key if isinstance(it, ItemInstance) else it
            if key == item.key:
                inv_obj = it
                break
        if inv_obj is None:
            return None
        if item.ion_value is None:
            return None
        self.inventory.remove(inv_obj)
        self.ions += item.ion_value
        return item
