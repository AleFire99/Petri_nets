# E1 · Turnstile with counters (beginner)

**Goal:** write a first EFSM with context and run it.
**Read first:** [EFSM formal](../../docs/fsm/efsm-formal.md) sections 1–3, [regular FSM](../../docs/fsm/regular.md); run `examples/efsm_vending.py`.

A turnstile is `locked` or `unlocked`. It counts `coins` and `passages`. A `coin` unlocks it (an extra coin while unlocked is kept); a `push` while unlocked lets one person through and locks it; a `push` while locked does nothing.

1. Write the EFSM tuple and the transition table.
2. Implement `turnstile() -> EFSM` with the engine in `petrilab.fsm.efsm`.
3. Run `coin, push, push, coin, coin, push`. Which `send` calls return `False`? Final configuration?
4. State the invariant relating `passages` and `coins` and check it with `explore(..., max_depth=8)`.
5. In strict mode, what does `push` in `locked` do? Is the configuration changed?

**Check yourself:** final configuration `locked` with 3 coins. Solution: [`e1_turnstile.py`](../solutions/e1_turnstile.py).
