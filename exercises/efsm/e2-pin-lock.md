# E2 · PIN lock: guards and edge cases (intermediate)

**Goal:** design mutually exclusive guards, test boundaries, verify exhaustively.
**Read first:** [EFSM formal](../../docs/fsm/efsm-formal.md) sections 2 and 4.

A lock opens with PIN `1234`. Three wrong PINs in a row block it until `admin_reset`. A correct PIN resets the counter. `lock` re-locks an open lock.

1. Write the transition table with guards on `enter(pin)` that are **mutually exclusive and complete** (no priority needed).
2. Implement `pin_lock() -> EFSM`.
3. Test the edges: 2 wrong PINs (not blocked), 3rd wrong (blocked), correct after 2 wrong (counter reset), correct PIN while blocked (ignored).
4. Explore with events `enter(1234)`, `enter(1111)`, `lock`, `admin_reset`. How many configurations and edges? Any deadlock?
5. Write three invariants and check them. Confirm `nondeterministic_choices` is empty.

**Check yourself:** 5 configurations. Solution: [`e2_pin_lock.py`](../solutions/e2_pin_lock.py).
