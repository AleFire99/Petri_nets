# CLAUDE.md

## Commands
- `uv sync` — install deps
- `uv run pytest` — tests
- `uv run ruff check` / `uv run ruff format` — lint / format
- `uv run mypy src` — type check
- `cd fsm/xstate && npm run verify` — XState typecheck + export + analyze + vitest; commit `fsm/xstate/generated/`

## Layout
- `fsm/xstate/` — every FSM: XState v5 machines, explorer, vector/ST export (rules: `fsm/xstate/AGENTS.md`); `fsm/xstate/generated/` is read by pytest
- `src/petrilab/petri/` — Petri net implementations; `src/petrilab/fsm/` — only hand-written FSM implementations proven against XState vectors
- `tests/` — pytest tests, mirroring `src/`
- `petri/spikes/` — throwaway library evaluations backing the Petri docs
- `fsm/docs/`, `petri/docs/` — designs (Markdown + fenced Mermaid; no committed images)

## Git flow
One feature branch per phase (`feat/…`, `docs/…`, `chore/…`), Conventional Commits, PR to `main`, squash merge.

## CI
`.github/workflows/ci.yml`: lint (ruff, format, mypy), tests, coherence (`uv lock --check`, `scripts/check_docs.py`, spikes run), Mermaid rendering, xstate (typecheck, generated files up to date, analyze, vitest). Run the first three locally before pushing; `uv run python scripts/check_docs.py` for docs.
