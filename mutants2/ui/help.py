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

COMMANDS_HELP = """Commands: look, north, south, east, west, last, travel, class (or x), inventory, get, drop, convert, exit, macro, @name, do

Look
----
• `look` — describe the current room.
• `look <dir>` — peek into an adjacent room; `<dir>` accepts any 1..full prefix:
  `look n` / `look no` / `look nor` / `look north` (same for s/so/sou/south, e/ea/eas/east, w/we/wes/west).
• `look <item>` — inspect a ground or inventory item by unique prefix.
• `look <monster>` — inspect a visible monster (here or in an adjacent open room).
• Movement commands are stricter: use n/s/e/w or full north/south/east/west (no partials like “no”).
• If blocked or no such target: “You can’t look that way.”

Senses
------
• Monsters start passive. Entering their room triggers a 50/50 roll for each to aggro — success shows “<Name> yells at you!” and they’ll chase on later turns.
• LOOK takes a turn. Aggro’d monsters may move after each of your turns.
• You may see multiple shadow directions (“west, north”).
• “Faint … far to the <dir>” means farther away; “Loud … to the <dir>” means closer.
• When a monster enters your room you’ll see: “<Name> has just arrived from the <dir>.” and “<Name> is here.”

Audio
-----
• Monsters start passive and don’t move until they aggro.
• You hear footsteps only if an aggro’d monster actually moved that turn.
• A monster yells exactly once when it aggroes as you enter its room.

Debug
-----
• `help debug` — list developer-only commands for spawning items, monster tools, date overrides, etc.
"""


ABBREVIATIONS_NOTE = """Prefixes
---------
• Commands (except directions): use any prefix from the first 3 letters up to the full word.
  Examples: tra/trav/trave/travel 2000, inv, mac, hel, exi.
• Directions are special: movement commands use 1-letter (n/s/e/w) or the full word (north/south/east/west).
  For `look <dir>`, any 1..full prefix works.
• Targets (items/monsters) after a command accept any prefix from the first letter up to the full name.
  If multiple names match, the first in the list is used.
• For LOOK specifically, a name after 'look' prefers monsters over items. If neither matches, 'look <dir>' is tried.
"""
