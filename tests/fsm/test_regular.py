import pytest
from statemachine.exceptions import TransitionNotAllowed

from petrilab.fsm.regular import TrafficLight, Turnstile


def test_traffic_light_cycles() -> None:
    sm = TrafficLight()
    seen = []
    for _ in range(4):
        seen.append(next(iter(sm.configuration)).id)
        sm.send("next")
    assert seen == ["red", "green", "yellow", "red"]


@pytest.mark.parametrize(
    ("start", "event", "end"),
    [
        (["push"], "push", "locked"),
        ([], "coin", "unlocked"),
        ([], "push", "locked"),
        (["coin"], "coin", "unlocked"),
        (["coin"], "push", "locked"),
    ],
)
def test_turnstile_transitions(start: list[str], event: str, end: str) -> None:
    sm = Turnstile()
    for e in start:
        sm.send(e)
    sm.send(event)
    assert {s.id for s in sm.configuration} == {end}


def test_invalid_event_rejected() -> None:
    with pytest.raises(TransitionNotAllowed):
        Turnstile().send("kick")
