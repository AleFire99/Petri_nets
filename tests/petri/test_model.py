import pytest

from petrilab.petri import analysis, examples
from petrilab.petri.model import PTNet, StateSpaceLimitError
from petrilab.petri.snakes_bridge import explore, to_snakes


def test_fire_and_enabled() -> None:
    n = examples.water()
    m = n.initial_marking
    assert n.enabled_transitions(m) == ["react"]
    m2 = n.fire(m, "react")
    assert n.marking_dict(m2) == {"H2": 2, "O2": 1, "H2O": 2}
    with pytest.raises(ValueError):
        n.fire(n.marking(H2=1, O2=1), "react")


def test_unknown_place_rejected() -> None:
    n = PTNet("x")
    with pytest.raises(ValueError):
        n.add_transition("t", {"nope": 1})


def test_state_limit() -> None:
    n = examples.bounded_counter(inhibited=False)
    with pytest.raises(StateSpaceLimitError):
        n.reachable(max_states=50)


@pytest.mark.parametrize(
    "net",
    [
        examples.water(),
        examples.bounded_counter(),
        examples.read_arc_net(),
        examples.producer_consumer(3),
        examples.dining_philosophers(3),
        examples.dining_philosophers(3, atomic=True),
        examples.mutex(),
        examples.traffic_crossing(),
    ],
    ids=lambda n: n.name,
)
def test_own_engine_matches_snakes(net: PTNet) -> None:
    """Cross-check the hand-written firing rule against SNAKES: same state count and dead count."""
    own = net.reachable()
    space = explore(to_snakes(net))
    assert len(space) == len(own)
    own_dead = sum(1 for succ in own.values() if not succ)
    assert len(analysis.dead_markings(space)) == own_dead
    own_edges = sum(len(succ) for succ in own.values())
    assert space.graph.number_of_edges() == own_edges
