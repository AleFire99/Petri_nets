import pytest

from petrilab.petri import examples
from petrilab.petri.coverability import OMEGA, coverability_graph, format_marking
from petrilab.petri.model import PTNet, StateSpaceLimitError


def unbounded_producer() -> PTNet:
    """Producer without a capacity place: Buffer grows forever."""
    n = PTNet("unbounded_producer")
    n.add_place("Ready", 1)
    n.add_place("Buffer")
    n.add_transition("produce", {"Ready": 1}, {"Ready": 1, "Buffer": 1})
    n.add_transition("consume", {"Buffer": 1})
    return n


# -- normal cases ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "net",
    [
        examples.water(),
        examples.producer_consumer(2),
        examples.mutex(),
        examples.traffic_crossing(),
    ],
    ids=lambda n: n.name,
)
def test_bounded_net_graph_equals_reachability_graph(net: PTNet) -> None:
    cg = coverability_graph(net)
    assert cg.is_bounded()
    assert set(cg.markings) == set(net.reachable())


def test_unbounded_place_gets_omega() -> None:
    cg = coverability_graph(unbounded_producer())
    assert cg.unbounded_places() == ["Buffer"]
    assert cg.place_bound("Buffer") == OMEGA
    assert cg.place_bound("Ready") == 1
    assert sorted(format_marking(m) for m in cg.markings) == ["(1, 0)", "(1, ω)"]


def test_inhibitor_free_counter_is_unbounded() -> None:
    cg = coverability_graph(examples.bounded_counter(inhibited=False))
    assert not cg.is_bounded()


def test_place_bound_of_bounded_net() -> None:
    cg = coverability_graph(examples.producer_consumer(3))
    assert cg.place_bound("Buffer") == 3
    assert cg.place_bound("Free") == 3


def test_coverability_queries() -> None:
    cg = coverability_graph(unbounded_producer())
    assert cg.is_coverable({"Buffer": 1_000})
    assert not cg.is_coverable({"Ready": 2})
    cg = coverability_graph(examples.mutex())
    assert not cg.is_coverable({"Crit1": 1, "Crit2": 1})  # mutual exclusion


def test_dead_transition_detected() -> None:
    n = PTNet("dead")
    n.add_place("A", 1)
    n.add_place("B")
    n.add_transition("go", {"A": 1}, {"B": 1})
    n.add_transition("never", {"A": 2}, {"B": 1})
    assert coverability_graph(n).dead_transitions() == ["never"]


# -- edge cases -----------------------------------------------------------------------------
def test_net_without_transitions_has_single_node() -> None:
    n = PTNet("idle")
    n.add_place("P", 5)
    cg = coverability_graph(n)
    assert len(cg) == 1
    assert cg.edges[(5,)] == []


def test_source_transition_is_unbounded() -> None:
    n = PTNet("source")
    n.add_place("Out")
    n.add_transition("emit", post={"Out": 1})
    cg = coverability_graph(n)
    assert cg.unbounded_places() == ["Out"]
    assert cg.edges[(OMEGA,)] == [("emit", (OMEGA,))]  # omega self-loop


def test_read_arcs_allowed() -> None:
    cg = coverability_graph(examples.read_arc_net())
    assert cg.is_bounded()
    assert cg.place_bound("Key") == 1


# -- invalid input --------------------------------------------------------------------------
def test_inhibitor_arcs_rejected() -> None:
    with pytest.raises(ValueError, match="inhibitor"):
        coverability_graph(examples.bounded_counter(inhibited=True))


def test_unknown_place_in_query() -> None:
    with pytest.raises(ValueError, match="unknown places"):
        coverability_graph(examples.water()).is_coverable({"Nope": 1})


def test_node_limit() -> None:
    with pytest.raises(StateSpaceLimitError):
        coverability_graph(examples.dining_philosophers(4), max_nodes=5)
