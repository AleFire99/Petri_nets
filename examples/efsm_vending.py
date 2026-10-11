"""EFSM on the vending machine: run, invalid transitions, exploration, invariants.

Run: uv run python examples/efsm_vending.py
Design: docs/fsm/extended.md, theory: docs/fsm/efsm-formal.md.
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
    UnknownEventError,
    explore,
    nondeterministic_choices,
)
from petrilab.fsm.vending_machine import environment_events, vending_machine

INVARIANTS = {
    "credit never negative": lambda c: c.ctx["credit"] >= 0,
    "idle means no credit": lambda c: c.state != "idle" or c.ctx["credit"] == 0,
}


def buggy_vending_machine() -> EFSM:
    """Refund forgets to clear the credit: violates 'idle means no credit'."""
    good = vending_machine()

    def keep_credit(ctx: Context, ev: Event) -> Mapping[str, Any]:
        return {}

    transitions = [
        Transition(t.source, t.event, t.target, t.guard, keep_credit, "/ (bug) nothing")
        if t.event == "refund"
        else t
        for t in good.transitions
    ]
    return EFSM(
        "buggyVending", good.states, good.initial, good.initial_context, transitions
    )


def main() -> None:
    print("-- run (docs/fsm/efsm-formal.md, section 3)")
    m = Machine(vending_machine())
    script: list[Event] = [
        {"type": "insert", "amount": 50},
        {"type": "select"},
        {"type": "insert", "amount": 50},
        {"type": "select"},
        {"type": "refund"},
        {"type": "select"},
    ]
    print(f"  start: {m.config}")
    for ev in script:
        fired = m.send(ev)
        print(f"  {ev}: {'fired' if fired else 'ignored'} -> {m.config}")

    print("\n-- invalid transitions")
    strict = Machine(vending_machine(), strict=True)
    try:
        strict.send("select")
    except InvalidTransitionError as exc:
        print(f"  strict: InvalidTransitionError: {exc}")
    try:
        strict.send("kick")
    except UnknownEventError as exc:
        print(f"  UnknownEventError: {exc}")

    print("\n-- exploration (coins 0/25/50/100, depth 4), same counts as XState")
    events = environment_events()
    r = explore(vending_machine(), events, max_depth=4)
    print(
        f"  configurations: {r.state_count}, edges: {r.edge_count}, frontier: {len(r.frontier)}"
    )
    print(
        f"  deadlocks: {len(r.deadlocks())}, invariant violations: {len(r.violations(INVARIANTS))}"
    )
    overlaps = nondeterministic_choices(vending_machine(), r, events)
    print(f"  overlapping guards resolved by priority: {len(overlaps)}, e.g.")
    config, ev_label, enabled = overlaps[0]
    print(f"    {config} on {ev_label}: {enabled}")

    print("\n-- buggy variant: refund keeps the credit")
    r = explore(buggy_vending_machine(), events, max_depth=4)
    violations = r.violations(INVARIANTS)
    shortest = min(violations, key=lambda v: len(v[2]))
    name, config, trace = shortest
    print(f"  {len(violations)} violating configurations; shortest counterexample:")
    print(f"    invariant '{name}' fails in {config} after {trace}")


if __name__ == "__main__":
    main()
