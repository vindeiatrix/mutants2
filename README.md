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

### Dev mode
Set `MUTANTS2_DEV=1` or run `python -m mutants2 --dev` to enable `debug` commands:

- `debug shadow <north|south|east|west>`
- `debug footsteps <1..4>`
- `debug clear`
Cues are shown on the next `look` and then consumed.
