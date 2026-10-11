"""Generic EFSM engine: semantics, invalid transitions, exploration."""

from collections.abc import Mapping
from typing import Any

import pytest

from petrilab.fsm.efsm import (
    EFSM,
    Configuration,
    Context,
    Event,
    InvalidTransitionError,
    Machine,
    Transition,
    UnknownEventError,
    event_label,
    explore,
    nondeterministic_choices,
)


def counter(limit: int = 2) -> EFSM:
    """Counts ``inc``; reaching ``limit`` moves to ``full``; ``reset`` goes back to zero."""

    def below(ctx: Context, ev: Event) -> bool:
        return bool(ctx["n"] + 1 < limit)

    def inc(ctx: Context, ev: Event) -> Mapping[str, Any]:
        return {"n": ctx["n"] + 1}

    return EFSM(
        "counter",
        states=("counting", "full"),
        initial="counting",
        context={"n": 0},
        transitions=[
            Transition(
                "counting", "inc", "counting", below, inc, "[n+1 < limit] / n++"
            ),
            Transition("counting", "inc", "full", None, inc, "[else] / n++"),
            Transition("full", "reset", "counting", None, lambda c, e: {"n": 0}),
        ],
    )


# -- normal behaviour -----------------------------------------------------------------------
def test_guards_and_priority() -> None:
    m = Machine(counter(2))
    assert m.send("inc") and m.config == Configuration.of("counting", {"n": 1})
    assert m.send("inc") and m.state == "full" and m.context == {"n": 2}
    assert m.trace == ["inc", "inc"]


def test_payload_events_and_dict_events_are_equivalent() -> None:
    from petrilab.fsm.vending_machine import vending_machine

    a, b = Machine(vending_machine()), Machine(vending_machine())
    a.send("insert", amount=25)
    b.send({"type": "insert", "amount": 25})
    assert a.config == b.config
    assert a.trace == ["insert(amount=25)"]


def test_step_is_pure() -> None:
    efsm = counter()
    c0 = efsm.initial_configuration
    c1 = efsm.step(c0, {"type": "inc"})
    assert c0.ctx == {"n": 0} and c1 is not None and c1.ctx == {"n": 1}


def test_reset_restores_initial_configuration() -> None:
    m = Machine(counter())
    m.send("inc")
    m.reset()
    assert m.config == m.efsm.initial_configuration and m.trace == []


def test_alphabet() -> None:
    assert counter().events == ("inc", "reset")


def test_event_label() -> None:
    assert event_label({"type": "select"}) == "select"
    assert event_label({"type": "insert", "amount": 25}) == "insert(amount=25)"


# -- invalid transitions --------------------------------------------------------------------
def test_ignored_event_leaves_configuration_unchanged() -> None:
    m = Machine(counter())
    before = m.config
    assert m.send("reset") is False
    assert m.config == before and m.trace == []


def test_strict_mode_raises_on_ignored_event() -> None:
    m = Machine(counter(), strict=True)
    with pytest.raises(InvalidTransitionError, match="no transition for reset"):
        m.send("reset")
    assert m.state == "counting"  # failed send has no effect


def test_unknown_event_always_raises() -> None:
    with pytest.raises(UnknownEventError):
        Machine(counter()).send("explode")


def test_action_writing_undeclared_variable_raises() -> None:
    bad = EFSM("bad", ("a",), "a", {"x": 0},
               [Transition("a", "go", "a", None, lambda c, e: {"y": 1})])  # fmt: skip
    with pytest.raises(KeyError, match="undeclared"):
        Machine(bad).send("go")


@pytest.mark.parametrize(
    ("states", "initial", "context", "transitions", "message"),
    [
        (("a", "a"), "a", {}, [], "duplicate"),
        (("a",), "b", {}, [], "initial state"),
        (("a",), "a", {}, [Transition("a", "go", "z")], "unknown state"),
        (("a",), "a", {"xs": [1, 2]}, [], "hashable"),
    ],
)
def test_invalid_definitions(
    states: tuple[str, ...],
    initial: str,
    context: dict[str, Any],
    transitions: list[Transition],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        EFSM("x", states, initial, context, transitions)


# -- exploration ----------------------------------------------------------------------------
def test_explore_counts_and_no_deadlock() -> None:
    r = explore(counter(2), [{"type": "inc"}, {"type": "reset"}])
    # counting n=0, counting n=1, full n=2
    assert r.state_count == 3 and r.edge_count == 3
    assert r.deadlocks() == [] and not r.depth_limited
    assert r.visited_states() == {"counting", "full"}


def test_explore_finds_deadlock_with_trace() -> None:
    efsm = EFSM("trap", ("a", "b"), "a", {}, [Transition("a", "go", "b")])
    r = explore(efsm, [{"type": "go"}])
    (dead,) = r.deadlocks()
    assert dead.state == "b"
    assert [event_label(e) for e in r.path_to(dead)] == ["go"]


def test_depth_bound_marks_frontier_not_deadlock() -> None:
    r = explore(counter(10), [{"type": "inc"}], max_depth=2)
    assert r.state_count == 3 and r.depth_limited
    assert r.deadlocks() == []


def test_state_limit_truncates() -> None:
    r = explore(counter(100), [{"type": "inc"}], max_states=5)
    assert r.truncated and r.state_count == 5


def test_invariant_violation_reports_shortest_trace() -> None:
    r = explore(counter(2), [{"type": "inc"}, {"type": "reset"}])
    (v,) = r.violations({"n stays below 2": lambda c: c.ctx["n"] < 2})
    name, config, trace = v
    assert name == "n stays below 2"
    assert config == Configuration.of("full", {"n": 2})
    assert trace == ["inc", "inc"]


def test_nondeterministic_choices_listed() -> None:
    efsm = counter(2)
    events: list[Event] = [{"type": "inc"}, {"type": "reset"}]
    r = explore(efsm, events)
    found = nondeterministic_choices(efsm, r, events)
    # with n = 0 both `inc` transitions are enabled: [n+1 < limit] and [else]
    assert [(str(c), e) for c, e, _ in found] == [("counting {n=0}", "inc")]
