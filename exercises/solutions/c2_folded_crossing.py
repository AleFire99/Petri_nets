"""Solution C2 (intermediate): fold a P/T net into a CPN. Statement: exercises/cpn/c2-folded-crossing.md

Answers:
1. ROAD = {"NS", "EW"}, variable r : ROAD. Places Red : ROAD (initially 1`NS ++ 1`EW),
   Green : ROAD (empty), Safe : UNIT (one token). Transitions go<r>: Red r + Safe -> Green r,
   stop<r>: Green r -> Red r + Safe.
2. Same state space as examples.traffic_crossing(): 3 markings, 4 edges, no deadlock.
3. The folded net does not change when roads are added: only the colour set grows.
   n roads: n + 1 markings (all red, or exactly one green).
4. Unfolded P-invariant Safe + sum_r Green[r] = 1: at most one road is green.
"""

from petrilab.petri import examples
from petrilab.petri.cpn import CPN, UNIT, ColourSet, const, unfold, var
from petrilab.petri.invariants import is_place_invariant


def crossing(roads: tuple[str, ...] = ("NS", "EW")) -> CPN:
    road = ColourSet("ROAD", roads)
    net = CPN(f"crossing_{len(roads)}")
    net.add_place("Red", road, roads)
    net.add_place("Green", road)
    net.add_place("Safe", UNIT, [()])
    r = {"r": road}
    net.add_transition(
        "go",
        variables=r,
        inputs={"Red": var("r"), "Safe": const(())},
        outputs={"Green": var("r")},
    )
    net.add_transition(
        "stop",
        variables=r,
        inputs={"Green": var("r")},
        outputs={"Red": var("r"), "Safe": const(())},
    )
    return net


def check() -> None:
    folded = crossing().reachable()
    pt = examples.traffic_crossing().reachable()
    assert len(folded) == len(pt) == 3
    assert sum(map(len, folded.values())) == sum(map(len, pt.values())) == 4
    assert all(folded.values())

    for roads in [("A",), ("A", "B", "C"), ("N", "S", "E", "W")]:
        net = crossing(roads)
        assert len(net.reachable()) == len(roads) + 1
        unfolded = unfold(net)
        y = {"Safe": 1, **{f"Green[{r!r}]": 1 for r in roads}}
        assert is_place_invariant(unfolded, y)


if __name__ == "__main__":
    check()
    print(
        "C2 OK: markings for 1..4 roads:",
        [len(crossing(tuple("NSEW"[:k])).reachable()) for k in range(1, 5)],
    )
