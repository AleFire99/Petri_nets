# C4 · Resource ordering for the philosophers (advanced)

**Goal:** remove a deadlock by design and prove it for several sizes.
**Read first:** [CPN formal](../../docs/petri/cpn-formal.md) section 4; [P3](../petri/p3-lock-ordering.md).

1. For the naive philosophers with `n = 5`, find the dead marking and the shortest trace to it.
2. Build `ordered_philosophers(n)`: each philosopher takes the **lower-numbered** of its two forks first. Use arc expressions that compute the fork from the binding (or two guarded transitions; explain the trade-off).
3. Show there is no dead marking for `n = 2..5`.
4. Show the ordered net is live and the naive one is not (unfold, convert with `to_snakes`, use `analysis.is_live`).
5. Compare state counts naive vs ordered for `n = 2..5`. Explain why the ordering breaks circular wait.

**Check yourself:** the naive deadlock trace has 5 steps for `n = 5`. Solution: [`c4_resource_ordering.py`](../solutions/c4_resource_ordering.py).
