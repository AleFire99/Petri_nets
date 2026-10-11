# CLAUDE.md

## Commands
- `uv sync` — install deps
- `uv run pytest` — tests
- `uv run ruff check` / `uv run ruff format` — lint / format
- `uv run mypy src examples exercises/solutions` — type check
- `cd xstate && npm run verify` — XState typecheck + export + analyze + vitest; commit `xstate/generated/`

## Layout
- `xstate/` — every FSM: XState v5 machines, explorer, vector/ST export (rules: `xstate/AGENTS.md`); `xstate/generated/` is read by pytest
- `src/petrilab/petri/` — Petri net implementations (P/T, coverability, CPN engine, ...); `src/petrilab/fsm/` — generic EFSM engine plus hand-written FSM implementations, each proven against XState vectors
- `tests/` — pytest tests, mirroring `src/`
- `spikes/petri/` — throwaway library evaluations backing the Petri docs
- `docs/fsm/`, `docs/petri/` — theory and designs (Markdown + fenced Mermaid; no committed images); `docs/references.md` — bibliography
- `study-plan.md` — curriculum; update it when adding a topic
- `examples/` — runnable scripts; expected stdout in `examples/expected/` (`UPDATE_EXPECTED=1 uv run pytest tests/test_example_scripts.py` after intended changes)
- `exercises/` — statements by topic, solutions in `exercises/solutions/` with a `check()` each (run by pytest)

## Git flow
One feature branch per phase (`feat/…`, `docs/…`, `chore/…`), Conventional Commits, PR to `main`, squash merge.

## CI
`.github/workflows/ci.yml`: lint (ruff, format, mypy), tests, coherence (`uv lock --check`, `scripts/check_docs.py`, spikes run), Mermaid rendering, xstate (typecheck, generated files up to date, analyze, vitest). Run the first three locally before pushing; `uv run python scripts/check_docs.py` for docs.
