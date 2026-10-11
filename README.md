# petrilab

A learning repo for designing and verifying finite state machines (FSMs, EFSMs), Petri nets and coloured Petri nets (CPNs). FSMs are designed, simulated and checked exhaustively in XState; Petri nets, CPNs and a small EFSM engine are implemented and analysed in Python. Every formalism finds deadlocks, and they agree where they overlap.

**Start here: [study plan](study-plan.md)**, ten modules from first definitions to a capstone, each with theory, runnable examples, code, tests and exercises.

## Learning objectives
1. State the formal definitions of P/T nets, CPNs and EFSMs and execute each by hand.
2. Analyse boundedness, deadlocks, liveness and invariants, and choose the right technique (reachability graph, coverability graph, invariants, state equation).
3. Fold P/T nets into CPNs and unfold CPNs into P/T nets.
4. Design deterministic EFSMs, verify invariants by exploration, read counterexamples.
5. Generate tests from a model and prove a hand-written implementation against them.
6. Implement all of it in typed, tested Python.

## Prerequisites
- Python basics (dataclasses, type hints, comprehensions) and pytest basics.
- Discrete maths: sets, functions, relations, graphs (BFS, strongly connected components), vectors and matrices.
- Helpful, not required: automata (DFA/NFA), a little TypeScript for the XState part.
- Tools: [uv](https://docs.astral.sh/uv/getting-started/installation/) (installs Python 3.13 itself), git; Node 22 for `xstate/`.

## Quick start

```bash
git clone https://github.com/AleFire99/Petri_nets.git && cd Petri_nets
uv sync                       # creates .venv with Python 3.13 and all dependencies from uv.lock
uv run pytest                 # all tests (engines, XState cross-checks, examples, exercise solutions)
uv run python examples/pt_firing_and_invariants.py   # a runnable example
uv run python exercises/solutions/p1_parking_lot.py  # an exercise solution
uv run jupyter lab            # notebooks in notebooks/petri/
```

`uv run` uses the project environment without activating it. To work in the venv directly: `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`), then plain `python` and `pytest`.

Quality checks (same as CI):

```bash
uv run ruff check && uv run ruff format --check
uv run mypy src examples exercises/solutions
uv run python scripts/check_docs.py      # links, indexes, code fences
uv lock --check                          # lockfile matches pyproject.toml

cd xstate && npm ci && npm run verify    # XState models: typecheck, export, analyze, vitest
```

Dependencies live in [`pyproject.toml`](pyproject.toml) and are pinned in [`uv.lock`](uv.lock). Add one with `uv add <pkg>` (or `uv add --dev <pkg>`). Need a `requirements.txt` for pip? `uv export --format requirements-txt --no-hashes > requirements.txt`.

PM4Py is AGPL v3, so it is an optional extra used only for the soundness cross-check: `uv sync --extra soundness` (or `pip install 'petrilab[soundness]'`). It is part of the `dev` group, so the tests and CI always have it. The core package does not import it.

## Layout

| Path | Content |
|------|---------|
| [`study-plan.md`](study-plan.md) | curriculum: modules, readings, checkpoints |
| [`docs/petri/`](docs/petri/README.md) | Petri theory ([foundations](docs/petri/foundations.md), [coverability](docs/petri/coverability.md), [CPN formal](docs/petri/cpn-formal.md)) and designs |
| [`docs/fsm/`](docs/fsm/README.md) | FSM designs and [EFSM theory](docs/fsm/efsm-formal.md) |
| [`docs/references.md`](docs/references.md) | books, papers, tools |
| [`src/petrilab/petri/`](src/petrilab/petri/) | P/T nets, analysis, invariants, coverability, CPN engine, timed, stochastic, hierarchical, workflow |
| [`src/petrilab/fsm/`](src/petrilab/fsm/) | generic EFSM engine, vending machine and fill station (proven against XState vectors) |
| [`tests/`](tests/) | pytest, mirroring `src/`, plus example and exercise checks |
| [`examples/`](examples/README.md) | runnable scripts with expected output |
| [`exercises/`](exercises/README.md) | 14 exercises, beginner to advanced, solutions in `exercises/solutions/` |
| [`xstate/`](xstate/README.md) | every FSM as an XState v5 machine, explorer, vector export |
| [`notebooks/petri/`](notebooks/petri/), [`spikes/petri/`](spikes/petri/) | interactive walkthroughs; library evaluations |

## Learning path

**FSMs (XState, TypeScript)**
1. **Workflow**: [`docs/fsm/xstate.md`](docs/fsm/xstate.md): design visually or as text, simulate, verify every state, export vectors / diagrams / ST.
2. **Designs**: [`docs/fsm/`](docs/fsm/README.md): regular, hierarchical, extended (guards), timed, history, parallel, Moore/Mealy, and a combined automation example ([fill station](docs/fsm/fill-station.md)).
3. **Code**: [`xstate/`](xstate/README.md), one machine per design. Python implementations ([`src/petrilab/fsm/`](src/petrilab/fsm/)): the fill station, and the vending machine on the generic EFSM engine, both proven against model vectors.

**Petri nets and CPNs (Python)**

4. **Theory**: [foundations](docs/petri/foundations.md), [coverability](docs/petri/coverability.md), [coloured nets](docs/petri/cpn-formal.md).
5. **Designs**: [`docs/petri/`](docs/petri/README.md): P/T, inhibitor/read arcs, coloured, timed, stochastic, hierarchical, workflow nets, classic examples.
6. **Libraries**: [`docs/petri/library-evaluation.md`](docs/petri/library-evaluation.md) with spikes in [`spikes/petri/`](spikes/petri/).
7. **Code**: [`src/petrilab/petri/`](src/petrilab/petri/) with tests in [`tests/petri/`](tests/petri/); notebooks in [`notebooks/petri/`](notebooks/petri/).

## Findings

| Topic | Result |
|-------|--------|
| FSM tooling | XState v5 replaces the earlier Python statechart libraries: visual editor, pure transition function for exhaustive checks, simulated clock ([decision record](docs/fsm/library-evaluation.md)). |
| Gotcha | XState keeps history in `historyValue`, outside value and context; an explorer that ignores it merges states that behave differently. |
| Petri library | SNAKES for nets and reachability, PM4Py for WF-net soundness; timed and stochastic semantics are hand-written (neither library provides them). |
| Gotcha | SNAKES omits empty places from markings and finds no firing modes for transitions without input arcs; the bridge handles both. |
| Verification | Deadlocks are dead markings in the reachability graph. The naive dining philosophers deadlock (everyone holds their left fork); taking both forks atomically is deadlock-free and live. |
| Cross-checks | The hand-written firing rule agrees with SNAKES on state/edge/dead counts; own soundness check agrees with PM4Py. |
| CPN engine | The hand-written CPN agrees with SNAKES on the jobs net; folded philosophers and mutex have the same state spaces as the P/T nets, and `unfold` gives isomorphic reachability graphs. |
| Coverability | Karp-Miller graphs equal the reachability graph for every bounded example net and put ω exactly on the growing places of unbounded ones. |
| Timed nets | With `serve` in [1,2] and `timeout` in [3,4], `timeout` never fires; it does with overlapping intervals. |
| Stochastic nets | M/M/1/K steady state from the CTMC matches the closed form (8, 4, 2, 1)/15. |
| XState vs Petri | Dining philosophers as parallel EFSM with forks in context: same state, edge and dead-state counts as the Petri net for n = 2, 3, 4. |
| Moore vs Mealy | Both detectors as regions of one XState machine: outputs agree in every reachable state (exact proof, replaces the earlier DFA-equivalence check). |
| XState vectors | Model-generated vectors (one per transition) pass on the hand-written Python `FillStation` and on the vending machine built with the Python EFSM engine (129/129); the Python explorer finds the same 53 configurations and 129 edges as XState at depth 4. |

Not adopted: SMT (`z3`) and external model checkers (TINA, LoLA, Romeo); they matter once state spaces stop fitting in memory.

Mermaid diagrams are fenced blocks (rendered by GitHub). To validate locally: `npx -y @mermaid-js/mermaid-cli -i docs/fsm/regular.md -o /tmp/out.md`.
