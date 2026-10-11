"""Karp-Miller coverability graph: unbounded vs bounded producer (docs/petri/coverability.md).

Run: uv run python examples/coverability_unbounded.py
"""

from petrilab.petri import examples
from petrilab.petri.coverability import coverability_graph, format_marking
from petrilab.petri.model import PTNet, StateSpaceLimitError


def unbounded_producer() -> PTNet:
    n = PTNet("unbounded_producer")
    n.add_place("Ready", 1)
    n.add_place("Buffer")
    n.add_transition("produce", {"Ready": 1}, {"Ready": 1, "Buffer": 1})
    n.add_transition("consume", {"Buffer": 1})
    return n


def show(net: PTNet) -> None:
    cg = coverability_graph(net)
    print(f"{net.name}: places {net.place_names}")
    for m, succ in cg.edges.items():
        arrows = ", ".join(f"{t} -> {format_marking(m2)}" for t, m2 in succ)
        print(f"  {format_marking(m)}: {arrows or 'dead'}")
    bounds = {
        p: ("ω" if cg.place_bound(p) == float("inf") else int(cg.place_bound(p)))
        for p in net.places
    }
    print(f"  bounded: {cg.is_bounded()}, bounds: {bounds}")


def main() -> None:
    net = unbounded_producer()
    show(net)
    print("  plain reachability does not terminate:")
    try:
        net.reachable(max_states=1_000)
    except StateSpaceLimitError as exc:
        print(f"    StateSpaceLimitError: {exc}")
    cg = coverability_graph(net)
    print(f"  coverable Buffer >= 1000: {cg.is_coverable({'Buffer': 1000})}")
    print(f"  coverable Ready >= 2: {cg.is_coverable({'Ready': 2})}")
    print()
    show(examples.producer_consumer(2))


if __name__ == "__main__":
    main()
