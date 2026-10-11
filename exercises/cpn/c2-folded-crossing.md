# C2 · Folding a P/T net (intermediate)

**Goal:** turn repeated P/T structure into colours.
**Read first:** [CPN formal](../../docs/petri/cpn-formal.md) sections 4–5; P/T net: `examples.traffic_crossing()` in [classic examples](../../docs/petri/examples.md).

The crossing has one `Safe` token and, per road (`NS`, `EW`), places `Red`, `Green` and transitions `go`, `stop`.

1. Fold it into a CPN with a colour set `ROAD` and one variable `r`. `Safe` is a `UNIT` place.
2. Compare markings and edges with the P/T net.
3. Add roads (`1`, `3`, `4` roads). How does the CPN change? How many markings for `n` roads?
4. Unfold the CPN and prove "at most one road is green" with a P-invariant on the unfolding.

**Check yourself:** 3 markings for 2 roads. Solution: [`c2_folded_crossing.py`](../solutions/c2_folded_crossing.py).
