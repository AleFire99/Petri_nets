# P1 · Parking lot (beginner)

**Goal:** build a first P/T net, fire it by hand, read the reachability graph.
**Read first:** [foundations](../../docs/petri/foundations.md) sections 1–4.

A car park has 3 spaces. Cars `arrive` (only if a space is free) and `leave`.

1. Draw the net with two places and two transitions. Write `M0`, `Pre`, `Post` and `C`.
2. List every reachable marking by hand. How many edges has the reachability graph?
3. Is the net safe? Bounded (with which k)? Deadlock-free? Live? Reversible?
4. Find a P-invariant and a T-invariant and say what each means for the car park.
5. Implement it with `PTNet` in a function `parking_lot(spaces: int = 3) -> PTNet` and check your answers with `net.reachable()`, `place_invariants`, `transition_invariants`.
6. Edge case: what happens with `spaces = 0`?

**Check yourself:** 4 markings. Solution: [`p1_parking_lot.py`](../solutions/p1_parking_lot.py).
