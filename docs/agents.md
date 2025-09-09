# Mutants2 — Agents & Single Source of Truth

This document defines the contracts our agents (and humans) must follow.  
**CI gates:** run `black .`, `ruff .`, `pyright`, and `pytest` before submitting changes.

## Guardrails (always on)
- **Canonical keys:** Use lowercase underscore keys in code/tests (e.g., `nuclear_rock`, `bug_skin`).
- **Breaking changes:** Bump `SAVE_SCHEMA` and start a fresh world; **do not write migrations**.
- **Determinism:** The world is deterministically seeded **only in the CLI entrypoint**; tests must use a **temporary SAVE_PATH** and opt-in seeding.
- **Worn ≠ inventory:** Worn items are not in inventory scope; use helpers like `resolve_item(prefix, scope="inventory"|"worn")`.

## Color palette & usage
- **green** — Compass line (e.g., `Compass: (0E : 0N)`).
- **header color** — Section titles like `On the ground lies:` and cardinal direction words (`north`, `south`, `east`, `west`).
- **item color** — Ground item names and exit description segments after the en-dash (e.g., `area continues.`).
- **yellow** — Generic feedback & help; prompts; “lovely” look-for-item line; inventory-scope failures (`You can't see <raw_subject>.`, `You're not carrying <raw_subject>.`); shadows header.
- **white** — Class selection menu; inventory list body; monster names shown in room renders (from look or `look <dir>`); monster taunts/native attacks (e.g., `Critter-750 bites you!`).
- **red** — Room header/description; kill/collect/drop/crumble lines; ion conversion feedback; monster arrival/leave; weapon/armor crack; ranged “blinding flash”; monster spell preamble; spell damage descriptions; monster picks up an item; monster converts an item to ions; monster drops an item.

Numbers are always plain (no commas).

## Core world & movement
- Each century is a **30×30** grid; edges block; center is **(0E : 0N)**.
- **Centuries enabled:** **2000–3000** inclusive, in 100-year steps.
- `travel <year>` lands at that century’s **center**; non-century input **rounds down** to the nearest in-range century and prints:  
  **`ZAAAAPPPPP!! You've been sent to the year {CENTURY} A.D.`**  
  If out-of-range, print the bounds message (“You can only travel from year 2000 to {max_century}!”).
- **Render gating:** **Movement re-renders; travel does not; `look` (no args) re-renders.**

## Input, targets, and UI
- Commands: **3..full** prefixes; `look <dir>`: **1..full**; item/monster targets: **1..full**; **first match wins**.
- Inventory/Status show **plain names** (no “+N”); enchantment is revealed via `look`.
- Numbers have **no commas**; use a global **A/An** article helper for messages.

## Look semantics
- `look` (no args): on-tile peek that can trigger aggro checks.
- `look <item>` searches **inventory only**.  
  – If found and spawnable: print **“It looks like a lovely <Title-Case Item-Name>!”**.
  – If not in inventory (on ground or worn): print using the raw token: **“You can't see `<raw_subject>`.”**
- `look <dir>` peeks without shadows.

## Aggro, footsteps, arrivals
- Monsters spawn **passive**; on room entry or `look` (no args) on a shared tile: **50/50** to aggro; on success, yell once: **“<Name> yells at you!”**.
- Only **aggro** monsters move one step after the player turn; if none aggro in-year, **skip** the movement tick.  
- **Footsteps:** loud at **2**, faint at **3–6**, none at **<1**; supports intermediate directions (e.g., “south-west”).  
- In an arrival tick, render arrivals last and **suppress** the generic presence line.

## Monsters, targeting, and rewards
- Multiple monsters can share a tile; names include a **unique 4-digit suffix** (e.g., `Mutant-1846`).
- **`combat <monster>`** selects a target (consumes a turn) and prints **“You’re ready to combat <Name>!”**; legacy `attack` is removed.
- Wielding hits only if **ready to combat** someone.
- On kill: award **20000 riblets** and **20000 ions**.

## Loot rules
- Every monster drops a Skull on death (placed on ground and announced).

## Inventory vs worn vs wield
- **Worn items are not inventory:** `drop/convert/wield/wear` **exclude worn**; only **`remove`** acts on worn.
- If both worn and carried copies exist, commands act on the **carried** copy.

## Armour Class (AC)
- **Natural AC from DEX:** `natural_dex_ac = 1 + floor(DEX/10)` (0–9→1, 10–19→2, 20–29→3, 30–39→4, …).
- **Total AC** = `natural_dex_ac + worn_armor_ac` and is recomputed on wear/remove, level/stat changes, world entry, and load.

## Ions: upkeep, heal, starvation
- **Per-class ion consumption** (per 10s) starts at **level 2** and is **additive** per the approved table (level 1 = 0).
- **Heal** uses the implemented class/level ion-cost formula; prints “Nothing Happens!” if already at max HP.
- **Starvation:** at 0 ions, every **10s** lose **1 HP per level** and print **“You’re starving for IONS!”**; ends when ions > 0 or on death.

## Profiles & saves
- Class menu order: **Thief, Priest, Wizard, Warrior, Mage**; **independent profiles** (year, coords, inventory, ions).
- First-time world entry per class grants **30000 ions**; “Ready to Combat” resets on death and on any exit.

## Speed Mode

Default checks are limited to `pyright` (basic) on `mutants2/`, `ruff`, `black`, and about ten smoke tests.
The full test suite lives in `tests/slow/` and runs only on demand or in the weekly maintenance workflow.
Do not re-expand the default checks unless required. Add new smoke tests only when new contracts must be locked.
