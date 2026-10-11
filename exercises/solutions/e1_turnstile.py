"""Solution E1 (beginner): turnstile EFSM with counters. Statement: exercises/efsm/e1-turnstile.md

Answers:
1. S = {locked, unlocked}, V = {coins, passages}, c0 = (0, 0), events coin, push.
   locked   --coin / coins += 1-->     unlocked
   unlocked --coin / coins += 1-->     unlocked   (extra coin is kept: a self-loop that
                                                    still changes the context)
   unlocked --push / passages += 1--> locked
   locked   --push-->                  (no transition: ignored, or error in strict mode)
2. Script coin, push, push, coin, coin, push ends in locked {coins=3, passages=2}.
3. Invariant passages <= coins holds in every configuration (each passage needs a coin
   since the last lock). Checked by bounded exploration.
4. Strict mode: push in locked raises InvalidTransitionError and leaves the configuration
   unchanged.
"""

from collections.abc import Mapping
from typing import Any

from petrilab.fsm.efsm import (
    EFSM,
    Context,
    Event,
    InvalidTransitionError,
    Machine,
    Transition,
    explore,
)


def add_coin(ctx: Context, ev: Event) -> Mapping[str, Any]:
    return {"coins": ctx["coins"] + 1}


def add_passage(ctx: Context, ev: Event) -> Mapping[str, Any]:
    return {"passages": ctx["passages"] + 1}


def turnstile() -> EFSM:
    return EFSM(
        "turnstile",
        states=("locked", "unlocked"),
        initial="locked",
        context={"coins": 0, "passages": 0},
        transitions=[
            Transition("locked", "coin", "unlocked", None, add_coin, "/ coins += 1"),
            Transition("unlocked", "coin", "unlocked", None, add_coin, "/ coins += 1"),
            Transition(
                "unlocked", "push", "locked", None, add_passage, "/ passages += 1"
            ),
        ],
    )


def check() -> None:
    m = Machine(turnstile())
    results = [m.send(ev) for ev in ["coin", "push", "push", "coin", "coin", "push"]]
    assert results == [True, True, False, True, True, True]  # 2nd push ignored
    assert m.state == "locked" and m.context == {"coins": 3, "passages": 2}

    r = explore(turnstile(), [{"type": "coin"}, {"type": "push"}], max_depth=8)
    assert (
        r.violations(
            {"passages <= coins": lambda c: c.ctx["passages"] <= c.ctx["coins"]}
        )
        == []
    )
    assert r.deadlocks() == []

    strict = Machine(turnstile(), strict=True)
    try:
        strict.send("push")
    except InvalidTransitionError:
        assert strict.state == "locked" and strict.context == {
            "coins": 0,
            "passages": 0,
        }
    else:
        raise AssertionError("push in locked must raise in strict mode")


if __name__ == "__main__":
    check()
    print("E1 OK")
