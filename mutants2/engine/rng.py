"""Deterministic helpers for monster AI.

The current movement logic no longer relies on randomness but
historically used a random shuffle.  This module is kept as a placeholder
so that imports remain stable and behaviour deterministic in tests.
"""

from __future__ import annotations

from typing import Iterable, Sequence, TypeVar, List

T = TypeVar("T")


def shuffle(seq: Sequence[T]) -> List[T]:
    """Return a deterministically shuffled copy of *seq*.

    The implementation simply returns ``list(seq)`` – callers expecting a
    random order will receive the original order, guaranteeing stable and
    testable behaviour.
    """

    return list(seq)
