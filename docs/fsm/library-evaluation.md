# FSM library evaluation

Versions and release dates were checked on PyPI on 2026-10-04. Spike code that exercises the features lives in [`spikes/fsm/`](../../spikes/fsm/) (run with `uv run python spikes/fsm/spike_<lib>.py`).

## Candidates

| Library | Version (release) | Notes |
|---------|-------------------|-------|
| [`transitions`](https://pypi.org/project/transitions/) | 0.9.3 (2025-07) | Mature, callback-centric; `HierarchicalMachine`, `Timeout` state feature, parallel states, graph extensions. Stable but slower release cadence. |
| [`python-statemachine`](https://pypi.org/project/python-statemachine/) | 3.2.1 (2026-08) | v3 added `StateChart`: compound, parallel, history, delayed events, SCXML-style semantics, Mermaid/Dot export, typed. Actively maintained. |
| [`sismic`](https://pypi.org/project/sismic/) | 1.6.13 (2026-09) | Full UML/SCXML-style statecharts in YAML; simulated clock; contracts and *property statecharts* for runtime verification; PlantUML export. |
| [`automata-lib`](https://pypi.org/project/automata-lib/) | 9.2.0 (2026-01) | Formal automata theory (DFA/NFA/PDA/TM): equivalence, minimisation. No hierarchy/guards/time. Useful for *analysing* flat FSMs, not for modelling statecharts. |
| `xstate-python` | not on PyPI | Does not exist as a published package; rejected. |
| [`statesman`](https://pypi.org/project/statesman/) | 1.0.5 (2024-05) | Async, `<3.13` only; stale; rejected. |
| `pytransitions` | 0.9.2 (2024-12) | Same project as `transitions` (extensions are bundled in it); not a separate choice. |

## Criteria matrix

Based on documentation and what the spikes actually demonstrated.

| Criterion | transitions | python-statemachine 3 | sismic | automata-lib |
|-----------|:-----------:|:---------------------:|:------:|:------------:|
| Flat FSM | yes | yes | yes | yes (DFA/NFA) |
| Hierarchy | yes (`HierarchicalMachine`) | yes (`State.Compound`) | yes | no |
| History (shallow/deep) | **no** (hand-rolled) | yes (`HistoryState`, spike OK) | yes (`shallow/deep history`, spike OK) | no |
| Guards + context | yes (`conditions`, model attrs) | yes (`cond=`, any attrs) | yes (Python expressions + context) | no |
| Timed transitions | yes (`Timeout`, real `threading.Timer`) | delayed events, **real clock only** | yes, **`SimulatedClock`** (`after(n)`) | no |
| Parallel regions | yes (`parallel=`) | yes (`State.Parallel`) | yes (`parallel states`) | no |
| Diagram export | graphviz/markup | **Mermaid**, Dot | PlantUML | graphviz |
| Typing | partial stubs | typed, `py.typed` | partial | typed |
| Verification support | none | none | contracts + property statecharts | equivalence, emptiness |
| Maintenance | moderate | active | active | active |
| Definition style | Python dicts / calls | Python class DSL | YAML (external) | Python objects |

## Findings from the spikes
- **python-statemachine**: nested class DSL is concise and reads like the diagram; deep history restored `wash.agitate` correctly; parallel regions worked. Gotchas: state ids must be globally unique (two `off` states in different regions collided silently in the configuration), and a state with no outgoing transitions needs to be `final`. Mermaid export works out of the box.
- **sismic**: YAML statecharts passed the timed test with a `SimulatedClock` (no alarm at t=29, alarm at t=30) and deep history restore. Most verbose, but the best test story for time.
- **transitions**: hierarchy, parallel and timeout worked; there is no history support, and timeouts are real wall-clock timers, which makes deterministic tests awkward.

## Decision

| Design | Library | Why |
|--------|---------|-----|
| Regular (traffic light, turnstile) | `python-statemachine` | Simplest declarative API; invalid events raise. |
| Hierarchical (media player) | `python-statemachine` | Compound states, parent transitions. |
| Extended (vending machine) | `python-statemachine` | Guards/actions as methods using plain attributes for context. |
| Timed (door alarm) | `sismic` | Only library with an injectable fake clock. |
| History (washing machine) | `python-statemachine` | Native shallow and deep history. |
| Parallel (text styles) | `python-statemachine` | `State.Parallel`. |
| Moore vs Mealy | plain Python tables + `python-statemachine` for Moore | Output models are a property of the design, not library features; keep them tiny and compare outputs. |

`transitions` is not selected: it matches `python-statemachine` on most axes, lacks history and has less deterministic timers. `automata-lib` is the right tool for DFA equivalence checks, e.g. comparing Moore and Mealy machines, but is not needed yet. Total runtime dependencies for the FSM phase: `python-statemachine` and `sismic`.
