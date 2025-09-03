# Mutants2 Codex Guide

## Project map
- `mutants2/` – game source. Entry points:
  - `__main__.py` – CLI startup.
  - `cli/shell.py` – command dispatch loop.
  - `engine/` – world, player, items, monsters, persistence.
- `tests/` – canonical test suite.
- `tests/smoke/` – fast deterministic smoke tests.
- `docs/` – documentation.

## Areas to avoid touching
- Anything under `tests/` except within `tests/smoke/` when adding new smoke tests.
- `mutants2/engine/*` contains core game logic; modify with care.

## Determinism
The game world and monster placement are driven by a single RNG seed. Both the
runtime and `testing_api.run_one` pass a `seed` which feeds into the world's
`global_seed`. Use the same seed to reproduce scenarios. The smoke tests rely on
this determinism; no footsteps or yells should appear unless aggro actually
occurs.

## Test strategy
- `make smoke` / `pytest -q tests/smoke` – runs in a few seconds and is used for
  pull requests and quick local checks.
- `make test` / `pytest` – full suite with slower, more exhaustive coverage.
- CI runs the smoke set on PRs and the full suite plus type checks on `main`.

## Style
- Code is formatted with **Black** and linted by **Ruff**.
- Use `make fmt` before committing and `make lint` in CI or locally.
- Prefer small commits with descriptive messages (present tense, imperative).

## Commit message style
```
feat: short summary in present tense

Longer description if necessary.
```
