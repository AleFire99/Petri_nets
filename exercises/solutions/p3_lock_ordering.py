"""Solution P3 (intermediate): deadlock from lock ordering. Statement: exercises/petri/p3-lock-ordering.md

Answers:
1. Opposite order (A: L1 then L2, B: L2 then L1): 6 markings, 1 dead marking, where A holds
   L1 and B holds L2. Shortest trace: a_first, b_first.
2. Same order (both take L1 first): 5 markings, deadlock-free and live. Global lock ordering
   breaks the circular wait (Coffman condition 4).
3. Lock invariants. Opposite order: L1 + A_has1 + A_crit + B_crit = 1 and
   L2 + A_crit + B_has1 + B_crit = 1. Same order: L1 + A_has1 + A_crit + B_has1 + B_crit = 1
   and L2 + A_crit + B_crit = 1. Each lock is free or held by exactly one process in *both*
   versions, so invariants alone do not reveal the deadlock: deadlock is a behavioural
   property and needs the reachability graph (or a siphon/trap argument).
"""

from collections.abc import Callable

from petrilab.petri import analysis
from petrilab.petri.invariants import is_place_invariant
from petrilab.petri.model import Marking, PTNet
from petrilab.petri.snakes_bridge import explore, to_snakes


def two_locks(*, same_order: bool) -> PTNet:
    """Process A takes L1 then L2; B takes L2 then L1 (or L1 then L2 if ``same_order``)."""
    b_first, b_second = ("L1", "L2") if same_order else ("L2", "L1")
    net = PTNet(f"two_locks_{'ordered' if same_order else 'opposite'}")
    net.add_place("L1", 1)
    net.add_place("L2", 1)
    for proc, (first, second) in {"A": ("L1", "L2"), "B": (b_first, b_second)}.items():
        p = proc.lower()
        net.add_place(f"{proc}_idle", 1)
        net.add_place(f"{proc}_has1")
        net.add_place(f"{proc}_crit")
        net.add_transition(
            f"{p}_first", {f"{proc}_idle": 1, first: 1}, {f"{proc}_has1": 1}
        )
        net.add_transition(
            f"{p}_second", {f"{proc}_has1": 1, second: 1}, {f"{proc}_crit": 1}
        )
        net.add_transition(
            f"{p}_release", {f"{proc}_crit": 1}, {f"{proc}_idle": 1, "L1": 1, "L2": 1}
        )
    return net


def is_dead(net: PTNet) -> Callable[[Marking], bool]:
    return lambda m: not net.enabled_transitions(m)


def check() -> None:
    bad = two_locks(same_order=False)
    graph = bad.reachable()
    dead = [m for m, s in graph.items() if not s]
    assert len(graph) == 6 and len(dead) == 1
    held = {p for p, n in bad.marking_dict(dead[0]).items() if n}
    assert held == {"A_has1", "B_has1"}  # circular wait: A holds L1, B holds L2
    assert bad.trace_to(is_dead(bad)) == ["a_first", "b_first"]

    good = two_locks(same_order=True)
    graph = good.reachable()
    assert len(graph) == 5 and all(graph.values())
    space = explore(to_snakes(good))
    assert analysis.is_live(space, set(good.transitions))

    # lock invariants hold in both versions (answer 3)
    assert is_place_invariant(bad, {"L1": 1, "A_has1": 1, "A_crit": 1, "B_crit": 1})
    assert is_place_invariant(bad, {"L2": 1, "A_crit": 1, "B_has1": 1, "B_crit": 1})
    assert is_place_invariant(
        good, {"L1": 1, "A_has1": 1, "A_crit": 1, "B_has1": 1, "B_crit": 1}
    )
    assert is_place_invariant(good, {"L2": 1, "A_crit": 1, "B_crit": 1})


if __name__ == "__main__":
    check()
    bad = two_locks(same_order=False)
    print("P3 OK: deadlock trace", bad.trace_to(is_dead(bad)))
