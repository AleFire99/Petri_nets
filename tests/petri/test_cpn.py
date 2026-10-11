"""Hand-written CPN engine: firing rule, reachability, unfolding, cross-checks."""

from collections import Counter

import pytest

from petrilab.petri import analysis, cpn_examples, examples
from petrilab.petri.colored import jobs_net
from petrilab.petri.cpn import (
    CPN,
    UNIT,
    ColourError,
    ColourSet,
    NotEnabledError,
    binding_label,
    const,
    dead_markings,
    format_marking,
    to_pt_marking,
    unfold,
    var,
)
from petrilab.petri.invariants import is_place_invariant
from petrilab.petri.snakes_bridge import explore

# -- firing rule ----------------------------------------------------------------------------


def test_enabled_bindings_respect_guard_and_tokens() -> None:
    net = cpn_examples.jobs()
    m0 = net.initial_marking
    assert net.enabled_bindings(m0, "square") == [{"n": 2}, {"n": 3}]


def test_fire_moves_coloured_tokens() -> None:
    net = cpn_examples.jobs()
    m1 = net.fire(net.initial_marking, "square", {"n": 3})
    assert net.tokens(m1, "Jobs") == Counter({1: 1, 2: 1})
    assert net.tokens(m1, "Results") == Counter({9: 1})
    assert format_marking(m1) == "Jobs={1, 2} Results={9}"


def test_multiset_multiplicity() -> None:
    cs = ColourSet("AB", ("a", "b"))
    net = CPN("ms")
    net.add_place("P", cs, ["a", "a", "b"])
    net.add_place("Q", cs)
    net.add_transition("pair", variables={"x": cs}, inputs={"P": lambda b: [b["x"]] * 2},
                       outputs={"Q": var("x")})  # fmt: skip
    m0 = net.initial_marking
    assert format_marking(m0) == "P={2`'a', 'b'} Q={}"
    assert net.enabled_bindings(m0, "pair") == [{"x": "a"}]
    m1 = net.fire(m0, "pair", {"x": "a"})
    assert net.tokens(m1, "P") == Counter({"b": 1})
    assert net.enabled_bindings(m1, "pair") == []


def test_firing_is_pure() -> None:
    net = cpn_examples.jobs()
    m0 = net.initial_marking
    net.fire(m0, "square", {"n": 2})
    assert net.initial_marking == m0
    assert net.tokens(m0, "Jobs") == Counter({1: 1, 2: 1, 3: 1})


def test_binding_label() -> None:
    assert binding_label("take", {"p": 1}) == "take<p=1>"
    assert binding_label("tick", {}) == "tick"


# -- reachability ---------------------------------------------------------------------------
def test_jobs_matches_snakes() -> None:
    graph = cpn_examples.jobs().reachable()
    space = explore(jobs_net())
    assert len(graph) == len(space) == 4
    (dead,) = dead_markings(graph)
    (snakes_dead,) = analysis.dead_markings(space)
    assert format_marking(dead) == "Jobs={1} Results={4, 9}"
    assert sorted(space.markings[snakes_dead]["Results"]) == [4, 9]


@pytest.mark.parametrize("n_phil", [2, 3, 4])
@pytest.mark.parametrize("atomic", [False, True], ids=["naive", "atomic"])
def test_folded_philosophers_equal_pt_net(n_phil: int, atomic: bool) -> None:
    folded = cpn_examples.philosophers(n_phil, atomic=atomic).reachable()
    pt = examples.dining_philosophers(n_phil, atomic=atomic).reachable()
    assert len(folded) == len(pt)
    assert sum(map(len, folded.values())) == sum(map(len, pt.values()))
    assert len(dead_markings(folded)) == sum(1 for s in pt.values() if not s)


def test_naive_philosophers_deadlock_trace() -> None:
    net = cpn_examples.philosophers(3)
    trace = net.trace_to(lambda m: not net.successors(m))
    assert trace == ["takeLeft<p=0>", "takeLeft<p=1>", "takeLeft<p=2>"]


def test_mutex_cpn_equals_pt_mutex() -> None:
    assert len(cpn_examples.mutex(2).reachable()) == len(examples.mutex().reachable())


def test_mutual_exclusion_holds_for_any_process_count() -> None:
    for n in (2, 3, 4):
        net = cpn_examples.mutex(n)
        for m in net.reachable():
            assert sum(net.tokens(m, "Crit").values()) <= 1


# -- unfolding ------------------------------------------------------------------------------
def test_unfold_names_and_structure() -> None:
    pt = unfold(cpn_examples.philosophers(2, atomic=True))
    assert "Fork[0]" in pt.places and "Think[1]" in pt.places
    assert pt.transitions["take<p=1>"].pre == {
        "Think[1]": 1,
        "Fork[1]": 1,
        "Fork[0]": 1,
    }


def test_unfold_skips_bindings_failing_guard() -> None:
    pt = unfold(cpn_examples.jobs())
    assert "square<n=0>" not in pt.transitions
    assert "square<n=1>" not in pt.transitions
    assert "square<n=2>" in pt.transitions


def test_unfolded_reachability_graph_is_isomorphic() -> None:
    cpn = cpn_examples.philosophers(3)
    pt = unfold(cpn)
    mapped = {to_pt_marking(cpn, pt, m) for m in cpn.reachable()}
    assert mapped == set(pt.reachable())


def test_unit_places_unfold_to_plain_names() -> None:
    pt = unfold(cpn_examples.mutex(2))
    assert "Mutex" in pt.places
    assert is_place_invariant(pt, {"Mutex": 1, "Crit[1]": 1, "Crit[2]": 1})


# -- edge and invalid cases -----------------------------------------------------------------
def test_transition_without_variables() -> None:
    net = CPN("unit")
    net.add_place("A", UNIT, [()])
    net.add_place("B", UNIT)
    net.add_transition("move", inputs={"A": const(())}, outputs={"B": const(())})
    m1 = net.fire(net.initial_marking, "move", {})
    assert net.enabled_bindings(m1, "move") == []
    assert len(net.reachable()) == 2


def test_fire_disabled_binding_raises() -> None:
    net = cpn_examples.jobs()
    with pytest.raises(NotEnabledError, match="not enabled"):
        net.fire(net.initial_marking, "square", {"n": 1})  # guard false
    with pytest.raises(NotEnabledError, match="not enabled"):
        net.fire(net.initial_marking, "square", {"n": 7})  # no token 7


def test_fire_incomplete_binding_raises() -> None:
    net = cpn_examples.jobs()
    with pytest.raises(NotEnabledError, match="misses variables"):
        net.fire(net.initial_marking, "square", {})


def test_fire_unknown_transition_raises() -> None:
    net = cpn_examples.jobs()
    with pytest.raises(KeyError):
        net.fire(net.initial_marking, "cube", {"n": 2})


def test_initial_token_outside_colour_set() -> None:
    net = CPN("bad")
    with pytest.raises(ColourError):
        net.add_place("P", ColourSet("BOOL", (True, False)), ["yes"])


def test_output_token_outside_colour_set() -> None:
    small = ColourSet("SMALL", (1, 2, 3))
    net = CPN("overflow")
    net.add_place("P", small, [3])
    net.add_transition("inc", variables={"x": small}, inputs={"P": var("x")},
                       outputs={"P": lambda b: [b["x"] + 1]})  # fmt: skip
    with pytest.raises(ColourError, match="not in SMALL"):
        net.reachable()


def test_construction_errors() -> None:
    net = CPN("dup")
    net.add_place("P", UNIT)
    with pytest.raises(ValueError, match="duplicate place"):
        net.add_place("P", UNIT)
    with pytest.raises(ValueError, match="unknown places"):
        net.add_transition("t", inputs={"Q": const(())})
    net.add_transition("t")
    with pytest.raises(ValueError, match="duplicate transition"):
        net.add_transition("t")
