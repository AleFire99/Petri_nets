"""Solution P1 (beginner): parking lot with 3 spaces. Statement: exercises/petri/p1-parking-lot.md

Answers:
1. Places Free (3), Occupied (0); arrive: Free -> Occupied; leave: Occupied -> Free.
2. Reachable markings (Free, Occupied): (3,0), (2,1), (1,2), (0,3): 4 markings, 6 edges.
3. 3-bounded, not safe; deadlock-free; live; reversible.
4. P-invariant (1, 1): Free + Occupied = 3. T-invariant (1, 1): arrive then leave.
"""

from petrilab.petri.invariants import place_invariants, transition_invariants
from petrilab.petri.model import PTNet


def parking_lot(spaces: int = 3) -> PTNet:
    net = PTNet(f"parking_{spaces}")
    net.add_place("Free", spaces)
    net.add_place("Occupied")
    net.add_transition("arrive", {"Free": 1}, {"Occupied": 1})
    net.add_transition("leave", {"Occupied": 1}, {"Free": 1})
    return net


def check() -> None:
    net = parking_lot()
    graph = net.reachable()
    assert set(graph) == {(3, 0), (2, 1), (1, 2), (0, 3)}
    assert sum(map(len, graph.values())) == 6
    assert all(graph.values()), "deadlock-free: every marking has a successor"
    assert max(max(m) for m in graph) == 3  # 3-bounded
    # reversible: M0 reachable from everywhere (the graph is a chain walked both ways)
    for m in graph:
        sub = PTNet("from_m")
        sub.add_place("Free", m[0])
        sub.add_place("Occupied", m[1])
        sub.transitions = net.transitions
        assert sub.trace_to(lambda x: x == net.initial_marking) is not None
    assert place_invariants(net) == [[1, 1]]
    assert transition_invariants(net) == [[1, 1]]
    # edge case: zero spaces -> nothing can ever happen
    assert parking_lot(0).reachable() == {(0, 0): []}


if __name__ == "__main__":
    check()
    print("P1 OK:", sorted(parking_lot().reachable()))
