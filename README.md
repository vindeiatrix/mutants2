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

## Contributing / Agents

See [Agents Playbook](docs/agents.md) for roles, guardrails, routing rules, CI gates, and checklists.

### Dev mode
Set `MUTANTS2_DEV=1` or run `python -m mutants2 --dev` to enable `debug` commands:

- `debug shadow <north|south|east|west>`
- `debug footsteps <1..4>`
- `debug clear`
- `debug today YYYY-MM-DD` / `debug today clear` to override the system date
- `debug topup` to force a daily item top-up run
The game also performs a deterministic daily top-up of ground items (about 5% of walkable tiles per year) the first time you play on a given real-world day.
Cues are shown on the next `look` and then consumed.
