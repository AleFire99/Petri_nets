# petrilab

A learning repo for designing and evaluating finite state machines (FSMs) and Petri nets.

1. Design FSM variants in Markdown + Mermaid (`docs/fsm/`).
2. Evaluate Python FSM libraries and implement each variant with the best-suited one.
3. Repeat for Petri nets, including correctness / deadlock verification (`docs/petri/`).

## Quick start

```bash
uv sync
uv run pytest
uv run ruff check
uv run mypy src
```
