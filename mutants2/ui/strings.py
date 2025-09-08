from .theme import green, red, white, COLOR_HEADER, COLOR_ITEM

# semantic color wrappers
room_header = red
compass_line = green
exits_dir = COLOR_HEADER
exits_desc = COLOR_ITEM
ground_header = COLOR_HEADER
ground_list = COLOR_ITEM
presence_line = white
shadows_line = COLOR_HEADER
help_text = COLOR_HEADER
generic_fb = COLOR_HEADER
convert_fb = red
kill_reward = red
arrival_line = red
spell_line = red

# string constants
GET_WHAT = "What do you want to get?"
DROP_WHAT = "What do you want to drop?"
NOT_ENOUGH_IONS_PORTAL = "You don't have enough ions to create a portal."
CANT_SEE = "You can't see {0}."


def not_carrying(raw: str) -> str:
    """Return the not-carrying message for ``raw``."""

    return generic_fb(f"You're not carrying {raw}.")
