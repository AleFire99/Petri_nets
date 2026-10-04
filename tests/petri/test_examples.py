import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from petrilab.petri import analysis, examples
from petrilab.petri.invariants import is_place_invariant, weighted_sum
from petrilab.petri.model import PTNet
from petrilab.petri.snakes_bridge import explore, to_snakes


def space_of(net: PTNet):  # type: ignore[no-untyped-def]
    return explore(to_snakes(net), token_cap=50)


# -- producer / consumer ------------------------------------------------------------------------
def test_producer_consumer_properties() -> None:
    n = examples.producer_consumer(2)
    s = space_of(n)
    assert analysis.is_bounded(s)
    assert analysis.max_tokens(s, "Buffer") == 2
    assert analysis.is_deadlock_free(s)
    assert analysis.is_live(s, set(n.transitions))
    assert is_place_invariant(n, {"Free": 1, "Buffer": 1})
    assert is_place_invariant(n, {"ProdIdle": 1})
    assert len(s) == 3


@given(capacity=st.integers(min_value=1, max_value=5))
@settings(max_examples=10, deadline=None)
def test_producer_consumer_any_capacity(capacity: int) -> None:
    n = examples.producer_consumer(capacity)
    g = n.reachable()
    assert len(g) == capacity + 1
    assert all(succ for succ in g.values())  # deadlock-free
    w = {"Free": 1, "Buffer": 1}
    assert {weighted_sum(n, w, m) for m in g} == {capacity}


# -- dining philosophers ------------------------------------------------------------------------
def test_naive_philosophers_deadlock_is_found() -> None:
    n = examples.dining_philosophers(2)
    s = space_of(n)
    dead = analysis.dead_markings(s)
    assert dead, "the naive protocol must have a deadlock"
    for key in dead:  # every dead marking: everyone holds their left fork, nobody eats
        assert all(s.tokens(key, f"HasLeft{i}") == 1 for i in range(2))
        assert all(s.tokens(key, f"Fork{i}") == 0 for i in range(2))
        assert all(s.tokens(key, f"Eat{i}") == 0 for i in range(2))
    assert not analysis.is_live(s, set(n.transitions))


def test_deadlock_reachable_by_firing_sequence() -> None:
    n = examples.dining_philosophers(2)
    m = n.initial_marking
    for t in ("takeLeft0", "takeLeft1"):
        m = n.fire(m, t)
    assert n.enabled_transitions(m) == []


def test_atomic_philosophers_are_deadlock_free_and_live() -> None:
    n = examples.dining_philosophers(2, atomic=True)
    s = space_of(n)
    assert analysis.is_deadlock_free(s)
    assert analysis.is_live(s, set(n.transitions))
    assert analysis.is_safe(s)
    assert is_place_invariant(n, {"Fork0": 1, "Eat0": 1, "Eat1": 1})
    assert is_place_invariant(n, {"Fork1": 1, "Eat1": 1, "Eat0": 1})


def test_neighbours_never_eat_together() -> None:
    n = examples.dining_philosophers(3, atomic=True)
    s = space_of(n)
    for k in s.graph:
        eating = [i for i in range(3) if s.tokens(k, f"Eat{i}")]
        assert len(eating) <= 1  # with 3 philosophers every pair are neighbours


@given(n_phil=st.integers(min_value=2, max_value=4))
@settings(max_examples=6, deadline=None)
def test_philosophers_any_size(n_phil: int) -> None:
    naive = examples.dining_philosophers(n_phil).reachable()
    fixed = examples.dining_philosophers(n_phil, atomic=True).reachable()
    assert any(not succ for succ in naive.values())
    assert all(succ for succ in fixed.values())


# -- mutual exclusion ---------------------------------------------------------------------------
def test_mutex_safety_and_liveness() -> None:
    n = examples.mutex()
    s = space_of(n)
    assert len(s) == 8
    assert all(s.tokens(k, "Crit1") + s.tokens(k, "Crit2") <= 1 for k in s.graph)
    assert analysis.is_deadlock_free(s)
    assert analysis.is_live(s, set(n.transitions))
    assert is_place_invariant(n, {"Mutex": 1, "Crit1": 1, "Crit2": 1})
    assert analysis.can_reach(s, lambda sp, k: sp.tokens(k, "Crit1") == 1)
    assert not analysis.can_reach(
        s, lambda sp, k: sp.tokens(k, "Crit1") == 1 and sp.tokens(k, "Crit2") == 1
    )


def test_broken_mutex_violates_safety() -> None:
    n = examples.mutex()
    broken = PTNet("broken")
    broken.places = dict(n.places)
    for t, spec in n.transitions.items():
        pre = {p: w for p, w in spec.pre.items() if p != "Mutex"}  # ignore the mutex
        post = {p: w for p, w in spec.post.items() if p != "Mutex"}
        broken.add_transition(t, pre, post)
    s = space_of(broken)
    assert any(s.tokens(k, "Crit1") + s.tokens(k, "Crit2") == 2 for k in s.graph)


# -- traffic crossing ---------------------------------------------------------------------------
def test_traffic_crossing_safety() -> None:
    n = examples.traffic_crossing()
    s = space_of(n)
    assert len(s) == 3
    assert all(s.tokens(k, "NS_Green") + s.tokens(k, "EW_Green") <= 1 for k in s.graph)
    assert analysis.is_deadlock_free(s)
    assert analysis.is_live(s, set(n.transitions))
    assert is_place_invariant(n, {"Safe": 1, "NS_Green": 1, "EW_Green": 1})
    assert is_place_invariant(n, {"NS_Red": 1, "NS_Green": 1})


# -- general: invariants hold on every reachable marking ----------------------------------------
@pytest.mark.parametrize(
    "net",
    [examples.producer_consumer(3), examples.mutex(), examples.traffic_crossing()],
    ids=lambda n: n.name,
)
def test_all_place_invariants_constant_on_reachable_markings(net: PTNet) -> None:
    from petrilab.petri.invariants import place_invariants

    invs = place_invariants(net)
    assert invs
    graph = net.reachable()
    for y in invs:
        w = dict(zip(net.place_names, y, strict=True))
        assert len({weighted_sum(net, w, m) for m in graph}) == 1
