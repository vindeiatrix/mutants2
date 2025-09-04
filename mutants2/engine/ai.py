from __future__ import annotations

from typing import MutableMapping, Optional

from ..ui.render import print_yell


def set_aggro(mon: MutableMapping[str, object]) -> Optional[str]:
    """Flip a monster to aggro and emit its yell once per aggro."""

    if not mon.get("aggro", False):
        mon["aggro"] = True
        mon["seen"] = True
        mon["has_yelled_this_aggro"] = False

    if not mon.get("has_yelled_this_aggro", False):
        mon["has_yelled_this_aggro"] = True
        return print_yell(mon)

    return None
