# P3 · Lock ordering deadlock (intermediate)

**Goal:** find a deadlock and its trace, fix it, and see what invariants can and cannot tell you.
**Read first:** [foundations](../../docs/petri/foundations.md) sections 3–5, [classic examples](../../docs/petri/examples.md); run `examples/reachability_deadlock.py`.

Two processes A and B share locks `L1`, `L2`. Each one loops: idle → take first lock → take second lock → critical section → release both. A takes `L1` then `L2`; B takes `L2` then `L1`.

1. Model it (places per process: `X_idle`, `X_has1`, `X_crit`; transitions `x_first`, `x_second`, `x_release`).
2. How many markings are reachable? Which are dead? Give the shortest firing sequence to a dead marking (`PTNet.trace_to`).
3. Fix it by making both processes take `L1` first. Show the fixed net is deadlock-free and live (`analysis.is_live` on `explore(to_snakes(net))`).
4. Write one P-invariant per lock for both versions. Do the invariants distinguish the broken net from the fixed one? What does that tell you about invariants and deadlocks?

**Check yourself:** the broken net deadlocks in 2 steps. Solution: [`p3_lock_ordering.py`](../solutions/p3_lock_ordering.py).
