# E4 · Test generation, mutants, and EFSM as CPN (advanced)

**Goal:** generate tests from a model, measure them with mutants, and connect EFSMs to CPNs.
**Read first:** [EFSM formal](../../docs/fsm/efsm-formal.md) sections 5–6, [XState workflow](../../docs/fsm/xstate.md); reuse `pin_lock()` from [E2](e2-pin-lock.md).

1. Write `transition_cover(efsm, events)`: one test vector per edge of the explored configuration graph (shortest path to the source, then the edge), each step with the expected `(state, context)`. This is what `npm run export` does for XState.
2. Write a plain-Python `PinLockImpl` (if/else, no engine) and show it passes every vector.
3. Make two mutants (block after 4 wrong PINs; do not reset the counter on success). Do your vectors kill them?
4. Encode the PIN lock as a CPN with one place `Ctrl` holding a single token `(state, attempts)` and one transition per event instance. Compare its reachable markings with the EFSM's configurations.

**Check yourself:** 8 vectors; both mutants killed. Solution: [`e4_test_generation.py`](../solutions/e4_test_generation.py).
