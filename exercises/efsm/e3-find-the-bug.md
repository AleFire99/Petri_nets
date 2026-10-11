# E3 · Find the bug by exploration (intermediate)

**Goal:** use bounded exploration and invariants as a bug finder, and learn its limits.
**Read first:** [EFSM formal](../../docs/fsm/efsm-formal.md) section 4, [extended FSM](../../docs/fsm/extended.md).

A colleague changed one line of the vending machine: in `has_credit`, `select` with `credit >= price` now goes to `idle` instead of staying in `has_credit`. Build that buggy machine from `vending_machine()` (copy its transitions and replace one `Transition`).

1. Write the three invariants of the vending machine as predicates on a `Configuration`.
2. Explore the buggy machine with coins `{25, 50}` up to depth 4. Report the shortest counterexample. Why is it guaranteed to be the shortest?
3. Repeat with depth 2. What does "no violation found" mean here?
4. Check the correct machine up to depth 6.
5. With coins `{25}` only, which depth do you need to find the bug? What does this say about choosing the environment events?

**Check yourself:** the counterexample has 3 events. Solution: [`e3_find_the_bug.py`](../solutions/e3_find_the_bug.py).
