# Mutants2

A tiny text adventure with a deterministic 30x30 map. The game currently only
supports the year 2000 and a single player wandering a maze.

## Running

```bash
python -m mutants2
```

## Testing

```bash
pytest
```

## Recent breaking changes

- Save schema bumped to `6`. Older saves are discarded on load and a fresh
  world is seeded automatically.
- Natural armour from Dexterity is now `1 + (DEX // 10)` and stacks with worn
  armour.
- Worn items are no longer counted in inventory; only `remove` operates on worn
  armour.
- `look <item>` only works for items in your inventory. Looking for an item on
  the ground or one you're wearing prints `You can't see <Item-Name>.` and does
  not refresh the room.
- The room view now only refreshes after movement/travel or a bare `look`.

### Dev mode
Set `MUTANTS2_DEV=1` or run `python -m mutants2 --dev` to enable `debug` commands:

- `debug shadow <north|south|east|west>`
- `debug footsteps <1..4>`
- `debug clear`
- `debug today YYYY-MM-DD` / `debug today clear` to override the system date
- `debug topup` to force a daily item top-up run
The game also performs a deterministic daily top-up of ground items (about 5% of walkable tiles per year) the first time you play on a given real-world day.
Cues are shown on the next `look` and then consumed.
