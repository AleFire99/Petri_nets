from petrilab.petri import analysis
from petrilab.petri.hierarchical import flatten, order_top, pay_subnet
from petrilab.petri.invariants import is_place_invariant
from petrilab.petri.snakes_bridge import explore, to_snakes


def test_flattened_structure() -> None:
    flat = flatten(order_top(), {"Pay": pay_subnet()})
    assert set(flat.places) == {"Ordered", "Pay.mid", "Paid", "Shipped"}
    assert set(flat.transitions) == {"Pay.authorise", "Pay.capture", "ship"}
    assert flat.transitions["Pay.authorise"].pre == {"Ordered": 1}
    assert flat.transitions["Pay.capture"].post == {"Paid": 1}


def test_flattened_behaviour_is_a_chain_ending_in_shipped() -> None:
    flat = flatten(order_top(), {"Pay": pay_subnet()})
    g = flat.reachable()
    assert len(g) == 4
    assert [m for m, s in g.items() if not s] == [flat.marking(Shipped=1)]
    space = explore(to_snakes(flat))
    assert analysis.is_safe(space)
    assert is_place_invariant(flat, dict.fromkeys(flat.places, 1))
