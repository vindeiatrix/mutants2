import re

from mutants2.engine.player import Player
from mutants2.ui.render import render_status
from mutants2.ui.theme import COLOR_ITEM


def strip(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def test_status_labels_use_item_color():
    p = Player(year=2000, clazz="Warrior")
    lines = render_status(p)
    rib_line = [ln for ln in lines if "Riblets" in ln][0]
    rib_label = COLOR_ITEM("Riblets      :")
    assert rib_line.startswith(rib_label)
    assert "\x1b[" not in rib_line.replace(rib_label, "")

    ion_line = [ln for ln in lines if "Ions" in ln][0]
    ion_label = COLOR_ITEM("Ions         :")
    assert ion_line.startswith(ion_label)
    assert "\x1b[" not in ion_line.replace(ion_label, "")
