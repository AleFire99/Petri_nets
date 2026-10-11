# P5 · Unbounded nets and the coverability graph (advanced)

**Goal:** analyse a net whose reachability graph is infinite.
**Read first:** [coverability](../../docs/petri/coverability.md); run `examples/coverability_unbounded.py`.

A server process `Run` (1 token) can `spawn` child jobs at any time (`Run → Run + Child`); a child can `finish` (`Child → Done`).

1. Build the Karp-Miller coverability graph by hand, then with `coverability_graph`. Which places are unbounded?
2. Show that `net.reachable()` does not terminate (catch `StateSpaceLimitError`).
3. Add a place `Slots` with `k = 3` tokens: `spawn` consumes a slot, `finish` returns it. Which places are bounded now? Give the P-invariant that proves it.
4. Change the design so that *every* place is bounded: the slot comes back only when a new transition `collect` removes a `Done` token. Prove boundedness with a P-invariant and confirm that the coverability graph equals the reachability graph.

**Check yourself:** the first coverability graph has 3 nodes. Solution: [`p5_coverability.py`](../solutions/p5_coverability.py).
