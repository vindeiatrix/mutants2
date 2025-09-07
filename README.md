# Mutants2

A tiny text adventure with a deterministic 30x30 map. The game currently only
supports the year 2000 and a single player wandering a maze.

> **Breaking change**: existing saves from earlier versions are no longer
> compatible.  The engine now enforces a strict save schema and will refuse to
> load unknown versions.  Use `debug reset` to remove the on-disk save file or
> `debug wipe` while in a session to clear in-memory state.

## Running

```bash
python -m mutants2
```

## Testing

```bash
pytest
```

### Dev mode
Set `MUTANTS2_DEV=1` or run `python -m mutants2 --dev` to enable `debug` commands:

- `debug shadow <north|south|east|west>`
- `debug footsteps <1..4>`
- `debug clear`
- `debug today YYYY-MM-DD` / `debug today clear` to override the system date
- `debug topup` to force a daily item top-up run
The game also performs a deterministic daily top-up of ground items (about 5% of walkable tiles per year) the first time you play on a given real-world day.
Cues are shown on the next `look` and then consumed.
