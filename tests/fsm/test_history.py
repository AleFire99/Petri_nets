import pytest
from statemachine.exceptions import TransitionNotAllowed

from petrilab.fsm.history import WasherDeep, WasherShallow


def ids(sm: WasherDeep | WasherShallow) -> set[str]:
    return {s.id for s in sm.configuration}


def run(sm: WasherDeep | WasherShallow, *events: str) -> None:
    for e in events:
        sm.send(e)


def test_deep_history_restores_exact_leaf() -> None:
    sm = WasherDeep()
    run(sm, "start", "filled", "soaked", "pause")
    assert ids(sm) == {"paused"}
    run(sm, "resume")
    assert ids(sm) == {"running", "wash", "agitate"}


def test_shallow_history_restores_default_child_of_wash() -> None:
    sm = WasherShallow()
    run(sm, "start", "filled", "soaked", "pause", "resume")
    assert ids(sm) == {"running", "wash", "soak"}


def test_history_for_simple_child() -> None:
    for cls in (WasherDeep, WasherShallow):
        sm = cls()
        run(sm, "start", "filled", "soaked", "washed", "pause", "resume")
        assert ids(sm) == {"running", "spin"}


def test_stop_from_paused() -> None:
    sm = WasherDeep()
    run(sm, "start", "pause", "stop")
    assert ids(sm) == {"off"}


def test_resume_when_not_paused_invalid() -> None:
    with pytest.raises(TransitionNotAllowed):
        WasherDeep().send("resume")
