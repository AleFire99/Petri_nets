from petrilab.petri.model import PTNet
from petrilab.petri.timed import explore_timed


def request_net(serve: tuple[int, int], timeout: tuple[int, int]) -> PTNet:
    n = PTNet("request")
    n.add_place("Req", 1)
    n.add_place("Served")
    n.add_place("TimedOut")
    n.add_transition("serve", {"Req": 1}, {"Served": 1}, interval=serve)
    n.add_transition("timeout", {"Req": 1}, {"TimedOut": 1}, interval=timeout)
    return n


def test_untimed_both_outcomes_reachable() -> None:
    n = request_net((1, 2), (3, 4))
    assert {"serve", "timeout"} <= {t for s in n.reachable().values() for t, _ in s}


def test_timeout_never_fires_when_serve_is_urgent() -> None:
    n = request_net((1, 2), (3, 4))
    space = explore_timed(n)
    assert space.fired == {"serve"}
    assert n.marking(TimedOut=1) not in space.markings
    assert n.marking(Served=1) in space.markings


def test_both_fire_with_overlapping_intervals() -> None:
    n = request_net((3, 5), (3, 4))
    space = explore_timed(n)
    assert space.fired == {"serve", "timeout"}


def test_serve_cannot_fire_before_earliest() -> None:
    n = request_net((2, 2), (5, 5))
    space = explore_timed(n)
    # firing edges out of the initial clock-0 state: none until two ticks passed
    start = next(
        s
        for s in space.states
        if s[0] == n.initial_marking and dict(s[1])["serve"] == 0
    )
    assert [lab for lab, _ in space.edges[start]] == ["tick"]


def test_persistent_clock_survives_unrelated_firing() -> None:
    n = PTNet("persist")
    n.add_place("A", 1)
    n.add_place("B", 1)
    n.add_place("A2")
    n.add_place("B2")
    n.add_transition("a", {"A": 1}, {"A2": 1}, interval=(1, 1))
    n.add_transition("b", {"B": 1}, {"B2": 1}, interval=(2, 2))
    space = explore_timed(n)
    assert n.marking(A2=1, B2=1) in space.markings
