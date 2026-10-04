from petrilab.petri import analysis, examples
from petrilab.petri.invariants import is_place_invariant, place_invariants, weighted_sum
from petrilab.petri.snakes_bridge import explore, to_snakes


def test_water_reachability_and_dead_marking() -> None:
    n = examples.water()
    g = n.reachable()
    assert set(g) == {
        n.marking(H2=4, O2=2),
        n.marking(H2=2, O2=1, H2O=2),
        n.marking(H2O=4),
    }
    dead = [m for m, s in g.items() if not s]
    assert dead == [n.marking(H2O=4)]


def test_water_target_reachable_and_not_live() -> None:
    n = examples.water()
    space = explore(to_snakes(n))
    assert analysis.is_bounded(space)
    assert not analysis.is_live(space, set(n.transitions))
    target = n.marking(H2O=4)
    assert target in n.reachable()
    assert n.marking(H2=1, O2=1, H2O=2) not in n.reachable()


def test_water_invariants() -> None:
    n = examples.water()
    assert is_place_invariant(n, {"H2": 1, "H2O": 1})
    assert is_place_invariant(n, {"O2": 2, "H2O": 1})
    assert not is_place_invariant(n, {"H2": 1, "O2": 1})
    assert len(place_invariants(n)) == 2
    for y in place_invariants(n):
        w = dict(zip(n.place_names, y, strict=True))
        assert len({weighted_sum(n, w, m) for m in n.reachable()}) == 1
