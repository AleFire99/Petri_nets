# Exercises

14 exercises, beginner to advanced. Statements are in `petri/`, `cpn/`, `efsm/`; worked solutions (code + answers in the module docstring) are in [`solutions/`](solutions/). Try each one before opening its solution.

```bash
uv run python exercises/solutions/p1_parking_lot.py   # run one solution (prints "P1 OK ...")
uv run pytest tests/test_exercise_solutions.py        # check every solution
```

Each solution exposes `check()`, which asserts the answers, so you can copy a solution's `check()` next to your own code to test it.

| # | Level | Exercise | Topic | Solution |
|---|-------|----------|-------|----------|
| P1 | beginner | [Parking lot](petri/p1-parking-lot.md) | first net, reachability, invariants | [py](solutions/p1_parking_lot.py) |
| P2 | beginner | [Traffic light](petri/p2-traffic-light.md) | state machine nets = FSMs, invalid firing | [py](solutions/p2_traffic_light.py) |
| P3 | intermediate | [Lock ordering](petri/p3-lock-ordering.md) | deadlock trace, fix, limits of invariants | [py](solutions/p3_lock_ordering.py) |
| P4 | intermediate | [Mutex invariants](petri/p4-mutex-invariants.md) | structural proof of mutual exclusion | [py](solutions/p4_mutex_invariants.py) |
| P5 | advanced | [Coverability](petri/p5-coverability.md) | Karp-Miller, ω, bounding by design | [py](solutions/p5_coverability.py) |
| P6 | advanced | [State equation](petri/p6-state-equation.md) | necessary vs sufficient conditions | [py](solutions/p6_state_equation.py) |
| C1 | beginner | [Odd jobs](cpn/c1-odd-jobs.md) | colour sets, guards, bindings, multisets | [py](solutions/c1_odd_jobs.py) |
| C2 | intermediate | [Folded crossing](cpn/c2-folded-crossing.md) | folding a P/T net, scaling by colours | [py](solutions/c2_folded_crossing.py) |
| C3 | intermediate | [Unfolding invariants](cpn/c3-unfolding-invariants.md) | invariants of a CPN via its unfolding | [py](solutions/c3_unfolding_invariants.py) |
| C4 | advanced | [Resource ordering](cpn/c4-resource-ordering.md) | deadlock removal, liveness for several n | [py](solutions/c4_resource_ordering.py) |
| E1 | beginner | [Turnstile](efsm/e1-turnstile.md) | first EFSM, ignored events, strict mode | [py](solutions/e1_turnstile.py) |
| E2 | intermediate | [PIN lock](efsm/e2-pin-lock.md) | exclusive guards, boundary tests, exploration | [py](solutions/e2_pin_lock.py) |
| E3 | intermediate | [Find the bug](efsm/e3-find-the-bug.md) | invariants, counterexamples, depth bounds | [py](solutions/e3_find_the_bug.py) |
| E4 | advanced | [Test generation](efsm/e4-test-generation.md) | transition coverage, mutants, EFSM as CPN | [py](solutions/e4_test_generation.py) |

Suggested order follows the [study plan](../study-plan.md).

## Adding an exercise
1. Statement `exercises/<topic>/<id>-<slug>.md` (goal, prerequisites, numbered tasks, "check yourself").
2. Solution `exercises/solutions/<id>_<slug>.py` with answers in the docstring and a `check()` function.
3. Add a row above. `tests/test_exercise_solutions.py` fails if a statement has no solution.
