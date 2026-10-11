"""Solution E2 (intermediate): PIN lock with guards and edge cases. Statement: exercises/efsm/e2-pin-lock.md

Answers:
1. S = {locked, unlocked, blocked}, V = {attempts}, events enter(pin), lock, admin_reset.
   | from     | event        | guard                          | action           | to       |
   | locked   | enter(pin)   | pin == SECRET                  | attempts = 0     | unlocked |
   | locked   | enter(pin)   | pin != SECRET and attempts < 2 | attempts += 1    | locked   |
   | locked   | enter(pin)   | pin != SECRET and attempts = 2 | attempts = 3     | blocked  |
   | unlocked | lock         |                                |                  | locked   |
   | blocked  | admin_reset  |                                | attempts = 0     | locked   |
   Guards on enter are mutually exclusive and complete: deterministic without priorities.
2. Edge cases: the 3rd wrong PIN blocks (not the 2nd, not the 4th); a correct PIN after two
   wrong ones unlocks and resets the counter; in blocked even the correct PIN is ignored.
3. Configurations with pins {SECRET, WRONG}: locked{0}, locked{1}, locked{2}, unlocked{0},
   blocked{3}: 5 configurations, 8 edges, no deadlock (blocked has admin_reset).
4. Invariants: attempts <= 3; blocked <=> attempts == 3; unlocked => attempts == 0.
"""

from collections.abc import Mapping
from typing import Any

from petrilab.fsm.efsm import (
    EFSM,
    Context,
    Event,
    Transition,
    explore,
    nondeterministic_choices,
)

SECRET = 1234
WRONG = 1111
MAX_WRONG = 3


def correct(ctx: Context, ev: Event) -> bool:
    return bool(ev["pin"] == SECRET)


def wrong_retry(ctx: Context, ev: Event) -> bool:
    return bool(ev["pin"] != SECRET and ctx["attempts"] < MAX_WRONG - 1)


def wrong_block(ctx: Context, ev: Event) -> bool:
    return bool(ev["pin"] != SECRET and ctx["attempts"] == MAX_WRONG - 1)


def reset(ctx: Context, ev: Event) -> Mapping[str, Any]:
    return {"attempts": 0}


def count(ctx: Context, ev: Event) -> Mapping[str, Any]:
    return {"attempts": ctx["attempts"] + 1}


def pin_lock() -> EFSM:
    return EFSM(
        "pinLock",
        states=("locked", "unlocked", "blocked"),
        initial="locked",
        context={"attempts": 0},
        transitions=[
            Transition("locked", "enter", "unlocked", correct, reset, "[pin ok] / attempts = 0"),
            Transition("locked", "enter", "locked", wrong_retry, count, "[wrong, attempts < 2] / attempts++"),
            Transition("locked", "enter", "blocked", wrong_block, count, "[wrong, attempts = 2] / attempts++"),
            Transition("unlocked", "lock", "locked"),
            Transition("blocked", "admin_reset", "locked", None, reset, "/ attempts = 0"),
        ],
    )  # fmt: skip


EVENTS: list[Event] = [
    {"type": "enter", "pin": SECRET},
    {"type": "enter", "pin": WRONG},
    {"type": "lock"},
    {"type": "admin_reset"},
]

INVARIANTS = {
    "attempts <= 3": lambda c: c.ctx["attempts"] <= MAX_WRONG,
    "blocked iff attempts == 3": lambda c: (c.state == "blocked") == (c.ctx["attempts"] == MAX_WRONG),
    "unlocked => attempts == 0": lambda c: c.state != "unlocked" or c.ctx["attempts"] == 0,
}  # fmt: skip


def check() -> None:
    from petrilab.fsm.efsm import Machine

    m = Machine(pin_lock())
    m.send("enter", pin=WRONG)
    m.send("enter", pin=WRONG)
    assert (
        m.state == "locked" and m.context["attempts"] == 2
    )  # 2nd wrong: not yet blocked
    m.send("enter", pin=SECRET)
    assert m.state == "unlocked" and m.context["attempts"] == 0  # counter reset

    m.reset()
    for _ in range(3):
        m.send("enter", pin=WRONG)
    assert m.state == "blocked" and m.context["attempts"] == 3  # 3rd wrong blocks
    assert m.send("enter", pin=SECRET) is False  # ignored while blocked
    m.send("admin_reset")
    assert m.state == "locked" and m.context["attempts"] == 0

    efsm = pin_lock()
    r = explore(efsm, EVENTS)
    assert r.state_count == 5 and r.edge_count == 8
    assert r.deadlocks() == [] and not r.depth_limited
    assert r.violations(INVARIANTS) == []
    assert nondeterministic_choices(efsm, r, EVENTS) == []  # guards are exclusive


if __name__ == "__main__":
    check()
    print("E2 OK:", sorted(str(c) for c in explore(pin_lock(), EVENTS).configurations))
