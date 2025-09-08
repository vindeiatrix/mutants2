# Agents

- Run `black .`, `ruff .`, `pyright`, `vulture`, and `pytest` before submitting changes.
- Use canonical item keys (lowercase with underscores) in code and tests.
- Breaking changes require bumping `SAVE_SCHEMA` and start a fresh world; do not write migrations.
- Item names in code remain plain; enchantment is revealed via `look`.
- The world is deterministically seeded only via the CLI; tests must use a temporary save path.
- Worn items are not part of inventory; use `resolve_item(prefix, scope)` for item lookups.
