# Petri net library evaluation

Versions and release dates were checked on PyPI on 2026-10-04. Spikes: [`petri/spikes/`](../spikes/) (`uv run python petri/spikes/spike_<lib>.py`).

## Candidates

| Tool | Version (release) | Role |
|------|-------------------|------|
| [`SNAKES`](https://pypi.org/project/snakes/) | 0.9.33 (2024-06) | Python Petri-net toolkit: coloured nets with Python expressions, guards, inhibitor/test arcs, state-graph (reachability) builder, PNML (`snakes.pnml`). Slow release cadence but stable, works on Python 3.13. |
| [`PM4Py`](https://pypi.org/project/pm4py/) | 2.7.23.8 (2026-09) | Process mining; Petri nets, PNML I/O, **WF-net soundness (Woflan)**, token replay. Heavy dependency tree (pandas, scipy, ...), prints a banner on import. P/T only (no colours/time). |
| `pnml` / `petrinet` / `petri-net-py` | not on PyPI | Do not exist as published packages; rejected. PNML I/O is covered by SNAKES and PM4Py. |
| [`networkx`](https://pypi.org/project/networkx/) | 3.7 (2026-09) | Graph analysis on a reachability graph (SCCs, reachability, cycles). Not a Petri-net library. |
| [`SimPy`](https://pypi.org/project/simpy/) | 4.1.2 (2026-05) | Discrete-event simulation, **not** a Petri-net formalism; no reachability analysis. Rejected. |
| [`z3-solver`](https://pypi.org/project/z3-solver/) / [`pysmt`](https://pypi.org/project/pysmt/) | 5.1.0.0 / 0.9.6 (2024-06) | SMT for symbolic checks (state-equation reachability, bounded model checking). Powerful but unnecessary at this scale; revisit for large nets. |
| `numpy`, `sympy`, `scipy` | current | Incidence matrix, P/T-invariants (integer nullspace), CTMC steady state. |
| TINA / LoLA / Romeo | external binaries, not installed here | Industrial model checkers via CLI. Not reproducible with `uv sync`; documented as a next step only. |

## Criteria matrix

| Criterion | SNAKES | PM4Py | networkx | z3 / pysmt |
|-----------|:------:|:-----:|:--------:|:----------:|
| Place/transition, weights | yes (multi-arcs) | yes (arc weights) | n/a | encode manually |
| Coloured tokens + guards | **yes** | no | n/a | encode manually |
| Inhibitor / read arcs | yes (`Inhibitor`, `Test`; weight-2 inhibitor verified) | no | n/a | encode manually |
| Timed / stochastic | no | no | n/a | no |
| Reachability graph | yes (`StateGraph`) | yes (coverability / woflan) | analysis only | symbolic |
| Deadlock (dead marking) | via graph (no successors) | WF-net only | via graph | via encoding |
| Boundedness / liveness | via graph / custom | WF-nets (soundness) | custom | custom |
| WF-net soundness | custom | **yes** (`check_soundness`) | custom | custom |
| P/T invariants | custom (numpy/sympy) | place invariants (Woflan output) | no | no |
| PNML I/O | yes | yes | no | no |
| Maintenance | slow, stable | very active | active | active / pysmt stale |

## Findings from the spikes
- **SNAKES**: all three feature checks passed. The water net gives 3 states; the coloured net gives 4 states; a weight-2 inhibitor arc bounds the counter at 3 states (0, 1, 2 tokens); a `Test` (read) arc leaves its token in place. `StateGraph.successors()` returns a generator, so dead markings are detected with `not any(True for _ in g.successors(i))`.
- **PM4Py**: `check_soundness` returns `True` for the parallel-review WF-net and `False` for the XOR/AND-mismatch net, with diagnostics (uncovered places, dead tasks). It needs a net built from `PetriNet.Place/Transition` and initial/final markings.
- Timed (TPN) and stochastic (SPN) semantics are in neither library, so both are implemented by hand (small, well-understood algorithms).

## Decision

| Need | Choice |
|------|--------|
| P/T, inhibitor/read, coloured, hierarchical (after flattening), classic examples | **SNAKES** nets + `StateGraph` |
| Deadlock / boundedness / safeness / liveness / reachable target | custom functions over the SNAKES reachability graph (using `networkx` for liveness via SCCs) |
| P/T-invariants | `sympy` integer nullspace of the incidence matrix |
| WF-net soundness | **PM4Py** `check_soundness` (cross-checked by own graph analysis) |
| Timed net | hand-written TPN explorer (integer-time semantics) |
| Stochastic net | SNAKES marking graph + `scipy`/`numpy` CTMC solve |
| Property tests | `hypothesis` |

SMT (`z3`) and the external tools (TINA/LoLA/Romeo) are deliberately not adopted; they matter once state spaces stop fitting in memory.
