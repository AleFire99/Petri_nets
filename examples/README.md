# Runnable examples

Each script is self-contained, deterministic and prints a short report. The exact expected output is in [`expected/`](expected/) and [`tests/test_example_scripts.py`](../tests/test_example_scripts.py) checks it on every test run.

```bash
uv run python examples/pt_firing_and_invariants.py      # one script
for f in examples/*.py; do uv run python "$f"; done     # all of them
UPDATE_EXPECTED=1 uv run pytest tests/test_example_scripts.py   # after an intended change
```

| Script | Shows | Theory | Expected output |
|--------|-------|--------|-----------------|
| [`pt_firing_and_invariants.py`](pt_firing_and_invariants.py) | incidence matrix, enabling, firing step by step, invalid firing, reachability graph, P/T-invariants, state equation | [foundations](../docs/petri/foundations.md) | [txt](expected/pt_firing_and_invariants.txt) |
| [`reachability_deadlock.py`](reachability_deadlock.py) | dining philosophers: dead marking and shortest trace, atomic fix is live; mutex safety and liveness | [examples](../docs/petri/examples.md) | [txt](expected/reachability_deadlock.txt) |
| [`coverability_unbounded.py`](coverability_unbounded.py) | Karp-Miller graph with ω, why plain reachability does not terminate, coverability queries | [coverability](../docs/petri/coverability.md) | [txt](expected/coverability_unbounded.txt) |
| [`cpn_bindings_and_unfolding.py`](cpn_bindings_and_unfolding.py) | CPN bindings and guards, firing coloured tokens, SNAKES cross-check, folded philosophers, unfolding to P/T | [CPN formal](../docs/petri/cpn-formal.md) | [txt](expected/cpn_bindings_and_unfolding.txt) |
| [`efsm_vending.py`](efsm_vending.py) | EFSM run, ignored and invalid events, bounded exploration (same counts as XState), overlapping guards, counterexample for a buggy variant | [EFSM formal](../docs/fsm/efsm-formal.md) | [txt](expected/efsm_vending.txt) |
| [`fill_station_behaviour.py`](fill_station_behaviour.py) | timed hierarchical EFSM: timers at `delay - 1` and `delay`, retries, lock-out, emergency stop | [fill station](../docs/fsm/fill-station.md) | [txt](expected/fill_station_behaviour.txt) |

Abridged sample (`efsm_vending.py`, buggy variant):

```text
-- buggy variant: refund keeps the credit
  24 violating configurations; shortest counterexample:
    invariant 'idle means no credit' fails in idle {credit=25, dispensed=0, rejected=0} after ['insert(amount=25)', 'refund']
```
