# petrilab

A learning repo for designing and evaluating finite state machines (FSMs) and Petri nets: design in Markdown + Mermaid, pick Python libraries with spike code, implement every design, and test it (including deadlock detection).

## Learning path

1. **FSM designs**: [`docs/fsm/`](docs/fsm/README.md): regular, hierarchical, extended (guards), timed, history, parallel, Moore/Mealy.
2. **FSM libraries**: [`docs/fsm/library-evaluation.md`](docs/fsm/library-evaluation.md) with runnable spikes in [`spikes/fsm/`](spikes/fsm/).
3. **FSM code**: [`src/petrilab/fsm/`](src/petrilab/fsm/) with tests in [`tests/fsm/`](tests/fsm/).
4. **Petri designs**: [`docs/petri/`](docs/petri/README.md): P/T, inhibitor/read arcs, coloured, timed, stochastic, hierarchical, workflow nets, classic examples.
5. **Petri libraries**: [`docs/petri/library-evaluation.md`](docs/petri/library-evaluation.md) with spikes in [`spikes/petri/`](spikes/petri/).
6. **Petri code**: [`src/petrilab/petri/`](src/petrilab/petri/) with tests in [`tests/petri/`](tests/petri/).

7. **Demo notebooks**: [`notebooks/fsm/`](notebooks/fsm/) and [`notebooks/petri/`](notebooks/petri/) walk through each implementation interactively (`uv run jupyter lab`).

## Findings

| Topic | Result |
|-------|--------|
| FSM library | `python-statemachine` 3 covers hierarchy, history, parallel regions, guards and Mermaid export; `sismic` is used for the timed machine because it has a simulated clock. `transitions` has no history and uses real timers. |
| Gotcha | `python-statemachine` state ids must be globally unique, even across parallel regions. |
| Petri library | SNAKES for nets and reachability, PM4Py for WF-net soundness; timed and stochastic semantics are hand-written (neither library provides them). |
| Gotcha | SNAKES omits empty places from markings and finds no firing modes for transitions without input arcs; the bridge handles both. |
| Verification | Deadlocks are dead markings in the reachability graph. The naive dining philosophers deadlock (everyone holds their left fork); taking both forks atomically is deadlock-free and live. |
| Cross-checks | The hand-written firing rule agrees with SNAKES on state/edge/dead counts; own soundness check agrees with PM4Py. |
| Timed nets | With `serve` in [1,2] and `timeout` in [3,4], `timeout` never fires; it does with overlapping intervals. |
| Stochastic nets | M/M/1/K steady state from the CTMC matches the closed form (8, 4, 2, 1)/15. |

Not adopted: SMT (`z3`) and external model checkers (TINA, LoLA, Romeo); they matter once state spaces stop fitting in memory.

## Quick start

```bash
uv sync
uv run pytest
uv run ruff check
uv run mypy src
```

PM4Py is AGPL v3, so it is an optional extra used only for the soundness cross-check: `uv sync --extra soundness` (or `pip install 'petrilab[soundness]'`). It is part of the `dev` group, so the tests and CI always have it. The core package does not import it.

Mermaid diagrams are fenced blocks (rendered by GitHub). To validate locally: `npx -y @mermaid-js/mermaid-cli -i docs/fsm/regular.md -o /tmp/out.md`.
