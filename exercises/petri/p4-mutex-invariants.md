# P4 · Proving mutual exclusion with invariants (intermediate)

**Goal:** prove a safety property structurally, without exploring states.
**Read first:** [foundations](../../docs/petri/foundations.md) section 5; net: `examples.mutex()` ([classic examples](../../docs/petri/examples.md)).

1. Compute `place_invariants(examples.mutex())`. Are all entries non-negative?
2. Find three semi-positive invariants (weights ≥ 0) and interpret each. Show each is a combination of the basis vectors (hint: `sympy.Matrix.gauss_jordan_solve`).
3. Derive `Crit1 + Crit2 ≤ 1` for every reachable marking from one of them. Why does this proof need no reachability graph?
4. Compute the T-invariants and interpret them.
5. Show that `Wait1 + Crit1` is **not** an invariant and say which transition breaks it.

**Check yourself:** the key invariant contains `Mutex`. Solution: [`p4_mutex_invariants.py`](../solutions/p4_mutex_invariants.py).
