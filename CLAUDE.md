# CLAUDE.md

## Commands
- `uv sync` — install deps
- `uv run pytest` — tests
- `uv run ruff check` / `uv run ruff format` — lint / format
- `uv run mypy src` — type check
- `cd xstate && npm run verify` — XState typecheck + export + analyze + vitest; commit `xstate/generated/`

## Layout
- `src/petrilab/fsm/`, `src/petrilab/petri/` — implementations
- `tests/` — pytest tests, mirroring `src/`
- `spikes/` — throwaway library evaluations backing the docs
- `docs/fsm/`, `docs/petri/` — designs and library evaluations (Markdown + fenced Mermaid; no committed images)
- `xstate/` — XState v5 models, explorer, vector/ST export (rules: `xstate/AGENTS.md`); `xstate/generated/` is read by pytest

## Git flow
One feature branch per phase (`feat/…`, `docs/…`, `chore/…`), Conventional Commits, PR to `main`, squash merge.

## CI
`.github/workflows/ci.yml`: lint (ruff, format, mypy), tests, coherence (`uv lock --check`, `scripts/check_docs.py`, spikes run), Mermaid rendering, xstate (typecheck, generated files up to date, analyze, vitest). Run the first three locally before pushing; `uv run python scripts/check_docs.py` for docs.
