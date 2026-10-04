# CLAUDE.md

## Commands
- `uv sync` — install deps
- `uv run pytest` — tests
- `uv run ruff check` / `uv run ruff format` — lint / format
- `uv run mypy src` — type check

## Layout
- `src/petrilab/fsm/`, `src/petrilab/petri/` — implementations
- `tests/` — pytest tests, mirroring `src/`
- `spikes/` — throwaway library evaluations backing the docs
- `docs/fsm/`, `docs/petri/` — designs and library evaluations (Markdown + fenced Mermaid; no committed images)

## Git flow
One feature branch per phase (`feat/…`, `docs/…`, `chore/…`), Conventional Commits, PR to `main`, squash merge.
