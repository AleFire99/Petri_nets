# P2 · Traffic light (beginner)

**Goal:** see that an FSM is a Petri net with one token.
**Read first:** [foundations](../../docs/petri/foundations.md) sections 2–5 and 7, [regular FSM](../../docs/fsm/regular.md).

A light cycles red → green → yellow → red.

1. Model it as a P/T net with places `Red`, `Green`, `Yellow` and transitions `go`, `slow`, `stop`.
2. Which subclass of nets is this (section 7)? Why is it "just an FSM"?
3. Compute the reachability graph, P-invariants and T-invariants. Interpret them.
4. Fire the T-invariant from `M0`. Where do you end up?
5. What happens if you try to fire `slow` in `M0`? Make your code show it (catch the exception).

**Check yourself:** one P-invariant, one T-invariant, 3 markings. Solution: [`p2_traffic_light.py`](../solutions/p2_traffic_light.py).
