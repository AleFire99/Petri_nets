"""Solution P5 (advanced): coverability and unboundedness. Statement: exercises/petri/p5-coverability.md

Answers:
1. Spawner (Run(1); spawn: Run -> Run + Child; finish: Child -> Done). Coverability graph:
     (1, 0, 0) -spawn-> (1, ω, 0)
     (1, ω, 0) -spawn-> (1, ω, 0), -finish-> (1, ω, ω)
     (1, ω, ω) -spawn-> (1, ω, ω), -finish-> (1, ω, ω)
   Child and Done are unbounded; Run is 1-bounded.
2. net.reachable() never terminates (it hits the state limit); the coverability graph has
   3 nodes.
3. Add Slots (k tokens): spawn consumes a slot, finish returns it. P-invariant
   Slots + Child = k gives Child <= k, but Done is still ω: finished children pile up.
4. Return the slot only when a `collect` transition removes a Done token. P-invariant
   Slots + Child + Done = k covers every growing place, so the net is bounded (Done <= k)
   and its coverability graph equals its reachability graph.
"""

from petrilab.petri.coverability import OMEGA, coverability_graph, format_marking
from petrilab.petri.invariants import is_place_invariant
from petrilab.petri.model import PTNet, StateSpaceLimitError


def spawner(slots: int | None = None, *, recycle: bool = False) -> PTNet:
    """``slots=None``: unlimited children. ``recycle``: slots come back only on collect."""
    net = PTNet("spawner")
    net.add_place("Run", 1)
    net.add_place("Child")
    net.add_place("Done")
    if slots is None:
        net.add_transition("spawn", {"Run": 1}, {"Run": 1, "Child": 1})
        net.add_transition("finish", {"Child": 1}, {"Done": 1})
        return net
    net.add_place("Slots", slots)
    net.add_transition("spawn", {"Run": 1, "Slots": 1}, {"Run": 1, "Child": 1})
    if recycle:
        net.add_transition("finish", {"Child": 1}, {"Done": 1})
        net.add_transition("collect", {"Done": 1}, {"Slots": 1})
    else:
        net.add_transition("finish", {"Child": 1}, {"Done": 1, "Slots": 1})
    return net


def check() -> None:
    cg = coverability_graph(spawner())
    assert sorted(format_marking(m) for m in cg.markings) == [
        "(1, 0, 0)",
        "(1, ω, 0)",
        "(1, ω, ω)",
    ]
    assert cg.unbounded_places() == ["Child", "Done"]
    try:
        spawner().reachable(max_states=500)
    except StateSpaceLimitError:
        pass
    else:
        raise AssertionError("reachability of an unbounded net must not terminate")

    cg = coverability_graph(spawner(3))
    assert cg.place_bound("Child") == 3
    assert cg.place_bound("Done") == OMEGA
    assert is_place_invariant(spawner(3), {"Slots": 1, "Child": 1})

    recycled = spawner(3, recycle=True)
    cg = coverability_graph(recycled)
    assert cg.is_bounded()
    assert cg.place_bound("Done") == 3
    assert is_place_invariant(recycled, {"Slots": 1, "Child": 1, "Done": 1})
    assert set(cg.markings) == set(recycled.reachable())  # bounded: same graph


if __name__ == "__main__":
    check()
    for m, succ in coverability_graph(spawner()).edges.items():
        print(format_marking(m), [(t, format_marking(m2)) for t, m2 in succ])
    print("P5 OK")
