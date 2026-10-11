"""Solution P2 (beginner): traffic light cycle. Statement: exercises/petri/p2-traffic-light.md

Answers:
1. Places Red (1), Green, Yellow; go: Red -> Green, slow: Green -> Yellow, stop: Yellow -> Red.
   It is a *state machine net* (one input, one output place per transition) with one token:
   exactly an FSM.
2. 3 markings, one cycle; safe; live; reversible; deadlock-free.
3. P-invariant Red + Green + Yellow = 1 (exactly one lamp). T-invariant (1, 1, 1).
4. Firing `slow` in M0 is invalid: Green is empty.
"""

from petrilab.petri.invariants import place_invariants, transition_invariants
from petrilab.petri.model import PTNet


def traffic_light() -> PTNet:
    net = PTNet("traffic_light")
    net.add_place("Red", 1)
    net.add_place("Green")
    net.add_place("Yellow")
    net.add_transition("go", {"Red": 1}, {"Green": 1})
    net.add_transition("slow", {"Green": 1}, {"Yellow": 1})
    net.add_transition("stop", {"Yellow": 1}, {"Red": 1})
    return net


def check() -> None:
    net = traffic_light()
    graph = net.reachable()
    assert list(graph) == [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    assert all(len(s) == 1 for s in graph.values())  # deterministic cycle, no deadlock
    assert all(sum(m) == 1 for m in graph)  # safe, one lamp
    assert place_invariants(net) == [[1, 1, 1]]
    assert transition_invariants(net) == [[1, 1, 1]]
    m = net.initial_marking
    for t in ["go", "slow", "stop"]:
        m = net.fire(m, t)
    assert m == net.initial_marking  # firing the T-invariant returns to M0
    try:
        net.fire(net.initial_marking, "slow")
    except ValueError:
        pass
    else:
        raise AssertionError("slow must not be enabled in M0")


if __name__ == "__main__":
    check()
    print("P2 OK:", list(traffic_light().reachable()))
