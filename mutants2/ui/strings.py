from .theme import green, cyan, blue, yellow, red, white

# semantic color wrappers
room_header = red
compass_line = green
exits_dir = cyan
exits_desc = blue
ground_header = yellow
ground_list = cyan
presence_line = white
shadows_line = yellow
help_text = yellow
generic_fb = yellow
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
