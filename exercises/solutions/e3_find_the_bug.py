"""Solution E3 (intermediate): find a bug by exploration. Statement: exercises/efsm/e3-find-the-bug.md

The buggy machine sends `select` with enough credit back to `idle` even when change remains
(target of the `enough` transition is idle instead of has_credit).

Answers:
1. Invariants: credit >= 0; idle => credit == 0; has_credit => credit > 0.
2. Coins {25, 50}, depth 4: the bug is found; the shortest counterexample is
   insert(amount=50), insert(amount=50), select -> idle {credit=25, dispensed=1, ...}.
   Breadth-first search guarantees no shorter trace exists.
3. With depth 2 the bug is not found: a bounded search proves nothing beyond its bound.
4. The fixed machine (petrilab.fsm.vending_machine) has no violation at depth 6.
5. Bonus: with coins {25} alone the bug needs 4 inserts: insert x4, select (credit 100 ->
   25), so depth >= 5. The environment model matters as much as the depth.
"""

from petrilab.fsm.efsm import EFSM, Event, Transition, explore
from petrilab.fsm.vending_machine import vending_machine

INVARIANTS = {
    "credit >= 0": lambda c: c.ctx["credit"] >= 0,
    "idle => credit == 0": lambda c: c.state != "idle" or c.ctx["credit"] == 0,
    "has_credit => credit > 0": lambda c: (
        c.state != "has_credit" or c.ctx["credit"] > 0
    ),
}


def buggy() -> EFSM:
    good = vending_machine()
    ts = []
    for t in good.transitions:
        if t.event == "select" and t.label.startswith("[credit >= price]"):
            t = Transition(
                t.source,
                t.event,
                "idle",
                t.guard,
                t.action,
                t.label + " (bug: -> idle)",
            )
        ts.append(t)
    return EFSM("buggyVending", good.states, good.initial, good.initial_context, ts)


def events(coins: tuple[int, ...]) -> list[Event]:
    return [
        *({"type": "insert", "amount": c} for c in coins),
        {"type": "select"},
        {"type": "refund"},
    ]


def shortest_violation(
    efsm: EFSM, coins: tuple[int, ...], depth: int
) -> list[str] | None:
    r = explore(efsm, events(coins), max_depth=depth)
    found = r.violations(INVARIANTS)
    if not found:
        return None
    return min((trace for _, _, trace in found), key=len)


def check() -> None:
    trace = shortest_violation(buggy(), (25, 50), 4)
    assert trace == ["insert(amount=50)", "insert(amount=50)", "select"]
    assert shortest_violation(buggy(), (25, 50), 2) is None
    assert shortest_violation(vending_machine(), (25, 50), 6) is None
    assert shortest_violation(buggy(), (25,), 4) is None
    assert shortest_violation(buggy(), (25,), 5) == ["insert(amount=25)"] * 4 + [
        "select"
    ]


if __name__ == "__main__":
    check()
    print("E3 OK: counterexample", shortest_violation(buggy(), (25, 50), 4))
