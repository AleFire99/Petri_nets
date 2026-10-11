# C3 · Invariants through unfolding (intermediate)

**Goal:** use P/T tools on a CPN via its unfolding.
**Read first:** [CPN formal](../../docs/petri/cpn-formal.md) section 5; net: `cpn_examples.philosophers(n)`.

1. Unfold the naive philosophers for `n = 3`. How many places and transitions? Predict, then check.
2. Write the per-philosopher invariant and check it with `is_place_invariant`.
3. Write the per-fork invariant. Hint: fork `f` is used by philosopher `f` (as left fork) and by philosopher `f − 1` (as right fork).
4. Show your `2n` invariants span the whole invariant space (compare with `len(place_invariants(...))`) for `n = 2, 3, 4`.
5. Derive "neighbours never eat at the same time" and check it on every reachable marking.

**Check yourself:** 12 places and 9 transitions for `n = 3`. Solution: [`c3_unfolding_invariants.py`](../solutions/c3_unfolding_invariants.py).
