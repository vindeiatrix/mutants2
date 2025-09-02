MACROS_HELP = """\
MACROS — define/run/edit command macros, with profiles
=====================================================

Basics
------
  macro add <name> = <script>      Define/replace a macro
  macro run <name> [args…]         Run a stored macro
  @<name> [args…]                  Quick-run (shorthand for macro run)
  do <script>                      Run a one-off script (not stored)
  macro list | show <name>         List names or show a script
  macro rm <name> | macro clear    Remove one or all macros (clear asks to confirm)
  macro echo on|off                Toggle echo of expanded commands (default: on)

Profiles (saved outside the savegame)
-------------------------------------
  macro save <profile>             Save to ~/.mutants2/macros/<profile>.json
  macro load <profile>             Load/merge from that file (overwrites same-name)
  macro profiles                   List available profiles
  Startup (optional):              Auto-load ~/.mutants2/macros/default.json if present

Script language
---------------
  • Separator:      Use ';' (newlines also act as ';')
  • Parameters:     $1 $2 ... $*  (all remaining words)
       e.g.,  macro add getn = get $*; north; look
  • Repeat single:  cmd*3          → cmd; cmd; cmd
  • Repeat group:   (cmd1; cmd2)*N → cmd1; cmd2; ... (N times)
  • Speed-walk:     tokens like 3n2e4w → n;n;n;e;e;w;w;w;w
       (valid dirs: n s e w; case-insensitive)
  • Wait:           wait <ms>      Pause for ms (capped at 2000)
  • Comments:       '#' to end of line is ignored

Safety & limits
---------------
  • No deep recursion: calls limited to depth ≤ 8
  • Expansion cap:    ≤ 1000 subcommands per run
  • On unknown subcommand or limit breach: stop with a clear error
  • Echo: when on, each expanded command prints as '> <cmd>'

Examples
--------
  macro add scout = look; n*2; look; e; look; (w; s)*2
  @scout

  macro add farm = (look; wait 150; get $1; wait 150)*5
  macro run farm Ion-Decay

  do 7e3n; look
"""

COMMANDS_HELP = """Commands: look, north, south, east, west, last, travel, class, inventory, get, drop, exit, macro, @name, do

Look
----
• `look` — describe the current room.
• `look <dir>` — peek into an adjacent room without moving. Example: `look n`, `loo west`.
• `look <item>` — inspect a ground or inventory item by unique prefix.
• `look <monster>` — inspect a visible monster (here or in an adjacent open room).
• If blocked or no such target: “You can’t look that way.”

Senses
------
• “A shadow flickers to the <dir>.” — a monster is in that adjacent open room.
• “You hear footsteps nearby.” — a monster moved within about four tiles this turn.
"""


ABBREVIATIONS_NOTE = """Prefixes
---------
• Commands (except directions): use any prefix from the first 3 letters up to the full word.
  Examples: tra/trav/trave/travel 2000, inv, mac, hel, exi.
• Directions are special: use 1-letter (n/s/e/w) or the full word (north/south/east/west).
• Targets (items/monsters) after a command accept any prefix from the first letter up to the full name.
  If multiple names match, the first in the list is used.
• For LOOK specifically, a name after 'look' prefers monsters over items. If neither matches, 'look <dir>' is tried.
"""

