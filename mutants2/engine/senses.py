from dataclasses import dataclass, field
from typing import Optional, Set, Literal

Direction = Literal["north", "south", "east", "west"]


@dataclass
class SensesCues:
    shadow_dirs: Set[Direction] = field(default_factory=set)
    footsteps_distance: Optional[int] = None

    def clear(self) -> None:
        self.shadow_dirs.clear()
        self.footsteps_distance = None


@dataclass
class SensesBuffer:
    """Ephemeral buffer; consumed on `look`."""

    _cues: SensesCues = field(default_factory=SensesCues)

    def add_shadow(self, direction: Direction) -> None:
        self._cues.shadow_dirs.add(direction)

    def set_footsteps(self, distance: int) -> None:
        if distance < 1 or distance > 4:
            raise ValueError("footsteps distance must be 1..4")
        self._cues.footsteps_distance = distance

    def clear(self) -> None:
        self._cues.clear()

    def pop(self) -> SensesCues:
        current = SensesCues(
            shadow_dirs=set(self._cues.shadow_dirs),
            footsteps_distance=self._cues.footsteps_distance,
        )
        self._cues.clear()
        return current
