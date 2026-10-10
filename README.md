# petrilab

A learning repo for designing and verifying finite state machines (FSMs) and Petri nets. FSMs are designed, simulated and checked exhaustively in XState; Petri nets are modelled and analysed in Python. Both find deadlocks, and they agree where they overlap.

## Learning path

**FSMs (XState, TypeScript)**
1. **Workflow**: [`docs/fsm/xstate.md`](docs/fsm/xstate.md): design visually or as text, simulate, verify every state, export vectors / diagrams / ST.
2. **Designs**: [`docs/fsm/`](docs/fsm/README.md): regular, hierarchical, extended (guards), timed, history, parallel, Moore/Mealy, and a combined automation example ([fill station](docs/fsm/fill-station.md)).
3. **Code**: [`xstate/`](xstate/README.md), one machine per design; the fill station also has a Python implementation ([`src/petrilab/fsm/`](src/petrilab/fsm/)) proven against model vectors.

**Petri nets (Python)**

4. **Designs**: [`docs/petri/`](docs/petri/README.md): P/T, inhibitor/read arcs, coloured, timed, stochastic, hierarchical, workflow nets, classic examples.
5. **Libraries**: [`docs/petri/library-evaluation.md`](docs/petri/library-evaluation.md) with spikes in [`spikes/petri/`](spikes/petri/).
6. **Code**: [`src/petrilab/petri/`](src/petrilab/petri/) with tests in [`tests/petri/`](tests/petri/); notebooks in [`notebooks/petri/`](notebooks/petri/) (`uv run jupyter lab`).

## Findings

| Topic | Result |
|-------|--------|
| FSM tooling | XState v5 replaces the earlier Python statechart libraries: visual editor, pure transition function for exhaustive checks, simulated clock ([decision record](docs/fsm/library-evaluation.md)). |
| Gotcha | XState keeps history in `historyValue`, outside value and context; an explorer that ignores it merges states that behave differently. |
| Petri library | SNAKES for nets and reachability, PM4Py for WF-net soundness; timed and stochastic semantics are hand-written (neither library provides them). |
| Gotcha | SNAKES omits empty places from markings and finds no firing modes for transitions without input arcs; the bridge handles both. |
| Verification | Deadlocks are dead markings in the reachability graph. The naive dining philosophers deadlock (everyone holds their left fork); taking both forks atomically is deadlock-free and live. |
| Cross-checks | The hand-written firing rule agrees with SNAKES on state/edge/dead counts; own soundness check agrees with PM4Py. |
| Timed nets | With `serve` in [1,2] and `timeout` in [3,4], `timeout` never fires; it does with overlapping intervals. |
| Stochastic nets | M/M/1/K steady state from the CTMC matches the closed form (8, 4, 2, 1)/15. |
| XState vs Petri | Dining philosophers as parallel EFSM with forks in context: same state, edge and dead-state counts as the Petri net for n = 2, 3, 4. |
| Moore vs Mealy | Both detectors as regions of one XState machine: outputs agree in every reachable state (exact proof, replaces the earlier DFA-equivalence check). |
| XState vectors | Model-generated vectors (one per transition) pass on the hand-written Python `FillStation`. |

Not adopted: SMT (`z3`) and external model checkers (TINA, LoLA, Romeo); they matter once state spaces stop fitting in memory.

## Quick start

```bash
uv sync
uv run pytest
uv run ruff check
uv run mypy src

cd xstate && npm ci && npm run verify   # XState models (Node 22)
```

PM4Py is AGPL v3, so it is an optional extra used only for the soundness cross-check: `uv sync --extra soundness` (or `pip install 'petrilab[soundness]'`). It is part of the `dev` group, so the tests and CI always have it. The core package does not import it.

Mermaid diagrams are fenced blocks (rendered by GitHub). To validate locally: `npx -y @mermaid-js/mermaid-cli -i docs/fsm/regular.md -o /tmp/out.md`.
