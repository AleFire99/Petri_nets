# FSM library evaluation (decision record)

## Decision (2026-10-10)
Design, simulate and verify every FSM in [XState v5](https://www.npmjs.com/package/xstate) (5.33.2; v6 is alpha only). Implement in the target language by hand and prove it against model-generated test vectors. Workflow: [xstate.md](xstate.md).

## Why
| Need | XState v5 | Best Python option found |
|------|-----------|--------------------------|
| Visual editing | VS Code extension and Stately Studio edit the diagram and write code back | none |
| Exhaustive checks (deadlock, blocking, invariants) | `transition()` is pure, so every state can be enumerated | none; libraries only execute |
| Deterministic time | `SimulatedClock` | sismic only |
| Hierarchy, history, parallel, guards, context | all native | python-statemachine 3 (no simulated clock) |
| Typing | `setup({ types })` | python-statemachine typed |

## What was tried first (2026-10-04, removed 2026-10-10)
Python implementations of designs 1–7 used `python-statemachine` 3.2.1 (hierarchy, history, parallel, guards, Mermaid export) and `sismic` 1.6.13 (the only one with a simulated clock, used for the timed design). `transitions` 0.9.3 was rejected: no history, real wall-clock timers. `automata-lib` 9.2.0 proved Moore/Mealy equivalence by DFA equality; the XState product-machine check now gives the same exact proof. Before removal, XState test vectors were replayed on the sismic door alarm (4/4) and the python-statemachine vending machine (129/129): the models agreed. The code is in git history before the commit that removed it.

Gotchas worth keeping:
- python-statemachine state ids must be globally unique, even across parallel regions.
- XState ignores events without a transition; python-statemachine (with `allow_event_without_transition = False`) raises.
