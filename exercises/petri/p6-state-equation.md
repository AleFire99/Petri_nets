# P6 · The state equation is not enough (advanced)

**Goal:** understand why `M = M0 + C·x` is necessary but not sufficient for reachability.
**Read first:** [foundations](../../docs/petri/foundations.md) sections 3 and 8.

Net: places `p1, p2, p3`; `t1: p1 → p2`; `t2: p2 → p1 + p3`; `M0 = (0, 0, 0)`.

1. Write the incidence matrix `C`.
2. Find all `x ∈ {0..5}²` with `M0 + C·x = (0, 0, 1)` (write `state_equation_solutions(net, target, bound)`).
3. Is `(0, 0, 1)` reachable? Explain the gap between 2 and 3.
4. Repeat with `M0 = (1, 0, 0)` and target `(1, 0, 1)`. Reachable now? With which sequence?
5. Which direction of the implication is useful in practice, and when?

**Check yourself:** exactly one solution in step 2. Solution: [`p6_state_equation.py`](../solutions/p6_state_equation.py).
