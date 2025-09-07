# Agents Playbook (mutants2)

> Single source of truth for how we plan, build, test, and ship changes using “agent” roles.
> This document encodes guardrails (canonical keys only, safe full reset), routing, CI gates, and checklists.

## 1) Agent roles

### Coding Agent
- **Owns:** Feature implementation, refactors, bug fixes.
- **Inputs:** Task spec, files-to-touch, acceptance.
- **Outputs:** PR with code + doc updates.
- **Success:** Smoke tests green; no new lints/types; UI parity rules respected.

### Test Agent
- **Owns:** Smoke/unit tests, fixtures, coverage.
- **Inputs:** Feature diff; user repro notes.
- **Outputs:** Tests that encode the contract and prevent regressions.
- **Success:** `pytest -q` green; coverage ≥ target; deterministic runs.

### Type/Schema Agent
- **Owns:** Types (`ItemInstance`, `MonsterInstance`, `SaveDoc`), persistence contract.
- **Inputs:** Proposed data shape changes.
- **Outputs:** Typed APIs, loader/saver, schema bumps.
- **Success:** `pyright` = 0; no invariance leaks; legacy data rejected by schema.

### Lint/Format Agent
- **Owns:** Black, Ruff, dead-code (“vulture”), pre-commit.
- **Inputs:** PR diffs.
- **Outputs:** Style fixes; lint/format config.
- **Success:** `black --check .` and `ruff` pass; no vulture finds (or justified ignores).

### Gameplay/Rules Agent
- **Owns:** Mechanics (combat, sense, UI order, color), prefix rules.
- **Inputs:** Design notes + original game captures.
- **Outputs:** Rule changes + docs.
- **Success:** Parity: room → compass → exits → ground → presence → shadows → arrivals; no commas; inventory/stats show **plain** names; `look` reveals enchant.

### Migration/Reset Agent
- **Owns:** State resets, `SAVE_SCHEMA`, debug nukes.
- **Inputs:** Breaking changes.
- **Outputs:** Schema bump + hard refusal of old saves; reseed on new game; reset utilities.
- **Success:** Clean starts; no crashy legacy keys; deterministic seeding in CLI only.

### Performance Agent
- **Owns:** Profiling, hot-path cleanup, memory/alloc tuning.
- **Inputs:** Slow traces; CI timing.
- **Outputs:** Targeted perf PRs; benchmarks.
- **Success:** Faster CI/runtime without behavior drift.

### Docs/Release Agent
- **Owns:** README, changelogs, task templates, release notes.
- **Inputs:** Merged PRs, breaking changes.
- **Outputs:** Clear docs + labeled PRs.
- **Success:** Contributors can follow process; releases are traceable.

---

## 2) Guardrails & conventions (must-follow)

- **Canonical keys only** for items/monsters; delete aliases/legacy keys.
- **No commas in numbers** anywhere.
- **Enchant visibility:** Inventory/Stats/echo = **plain name**; only `look` reveals “+N” aura text.
- **Command prefix rules:** 3..full for commands; 1..full for `look <dir>`; targets 1..full; first match wins.
- **Presence order:** Room (red) → Compass (green) → Exits (cyan) → `***` → Ground (yellow header + cyan list) → `***` → Presence (white) → `***` → Shadows (yellow) → Arrivals (red).
- **Travel:** runs on-entry aggro rolls only on landing tile; if no aggro in year → skip movement tick.
- **State resets:** exiting to class menu or quitting clears “Ready to Combat”.
- **UI rendering:** post-turn room block only for commands that should reprint (not `get`, etc.).

---

## 3) Routing rules

- **Feature/engine changes** → Coding Agent (consult Gameplay Agent if mechanics).
- **Type/persistence changes** → Type/Schema Agent; Migration Agent if breaking.
- **Failing tests** → Test Agent (may route to Coding Agent with minimal fix).
- **Black/Ruff/format errors** → Lint/Format Agent first.
- **Performance regressions** → Performance Agent.
- **Docs/templates** → Docs/Release Agent.

Label PRs/issues accordingly (`area:engine`, `area:types`, `ci:format`, `breaking`, etc.).

---

## 4) Build & CI gates (merge blockers)

- `black --check .` (no “would reformat” output).
- `ruff` (agreed rules; justify ignores inline).
- `pyright` (strict on `mutants2/*`; tests may be looser).
- `vulture` dead-code check (allowlist minimal).
- `pytest -q` (smoke + unit) with coverage ≥ **85%** (or current bar).
- CI must run all of the above; **any failure blocks merge**.

---

## 5) State management

- Maintain `SAVE_SCHEMA` (integer). On load, mismatch ⇒ refuse with a friendly message and instructions to start fresh.
- Provide `debug reset` (delete save path) and `debug wipe` (clear in-memory world/profiles).
- **Seeding:** `World()` does **not** auto-seed in tests; CLI entrypoint calls a `seed_for_cli(world)` helper; tests seed explicitly.

---

## 6) Test strategy

- **Smoke tests** encode external contracts (command echoes, UI order, footsteps/arrivals, aggro rules).
- **Unit tests** for functions with logic (matchers, formatters, resolvers).
- Fixtures must use **ephemeral SAVE_PATH** (tmp dir).
- Prefer deterministic seeding and fixed RNG seeds.
- When fixing a bug, add a test that fails pre-fix and passes post-fix.

---

## 7) Task & bug checklists

**Task PR checklist**
- [ ] Files to touch listed; acceptance written.
- [ ] Black/Ruff/Pyright/Vulture/Pytest all pass locally.
- [ ] README/Docs updated if behavior visible to users.
- [ ] Rollback: GitHub **Revert** plan noted.

**Bug fix checklist**
- [ ] Repro described; failing test added.
- [ ] Minimal fix applied; no unrelated refactors.
- [ ] Guardrails unaffected (keys, UI order, no commas).
- [ ] CI green.

---

## 8) Artifact map (where things live)

- **Registries:** `mutants2/data/items.py`, `mutants2/engine/monsters.py`
- **Types/schemas:** `mutants2/engine/types.py`
- **Persistence:** `mutants2/engine/persistence.py`
- **World/loop/AI/combat:** `mutants2/engine/world.py`, `engine/loop.py`, `engine/ai.py`, `engine/combat.py`
- **UI/Renderers:** `mutants2/ui/render.py`, `ui/items_render.py`, `ui/panels.py`, `ui/theme.py`, `ui/strings.py`
- **CLI:** `mutants2/cli/shell.py`
- **Tests:** `mutants2/tests/**`

---

## 9) Reusable snippets

**Safest-path directive** (paste into breaking tasks):
> Treat this change as *breaking*. Take the safest path: **full reset of game state**. Bump `SAVE_SCHEMA` and **refuse to load older saves** with a clear message. On first run for this change, **delete all existing players/profiles, inventories, monsters, and ground items**, then **reseed deterministically**. Provide/keep `debug reset` and `debug wipe`. Tests/CI use a **fresh ephemeral SAVE_PATH**. **No migrations** for legacy data.

**Task skeleton**

Task: <short title>
Goals

…

Files to touch

…

Implementation notes

…

Tests / Acceptance

…
