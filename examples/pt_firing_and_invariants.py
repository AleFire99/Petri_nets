"""P/T net basics on the producer/consumer net (docs/petri/foundations.md, section 6).

Run: uv run python examples/pt_firing_and_invariants.py
Shows: incidence matrix, enabling, firing step by step, an invalid firing, the reachability
graph, P- and T-invariants, and the state equation.
"""

from petrilab.petri import examples
from petrilab.petri.invariants import (
    place_invariants,
    transition_invariants,
    weighted_sum,
)


def main() -> None:
    net = examples.producer_consumer(2)
    print(f"net: {net.name}")
    print(f"places: {net.place_names}")
    print(f"M0 = {net.initial_marking}")

    print("\n-- incidence matrix C = Post - Pre (rows: places, columns: transitions)")
    for place, row in zip(net.place_names, net.incidence(), strict=True):
        print(f"  {place:<9} {row}")

    print("\n-- firing step by step")
    m = net.initial_marking
    for t in ["produce", "produce", "consume"]:
        print(f"  {m} enabled={net.enabled_transitions(m)} fire {t}")
        m = net.fire(m, t)
    print(f"  {m}")

    print("\n-- invalid firing: consume in M0 (Buffer is empty)")
    try:
        net.fire(net.initial_marking, "consume")
    except ValueError as exc:
        print(f"  ValueError: {exc}")

    print("\n-- reachability graph")
    graph = net.reachable()
    for marking, succ in graph.items():
        print(f"  {marking} -> {[(t, m2) for t, m2 in succ]}")
    dead = [mk for mk, s in graph.items() if not s]
    print(
        f"  {len(graph)} markings, {sum(map(len, graph.values()))} edges, dead: {dead}"
    )

    print("\n-- invariants")
    for y in place_invariants(net):
        terms = " + ".join(f"{w}*{p}" for p, w in zip(net.places, y, strict=True) if w)
        const = weighted_sum(
            net, dict(zip(net.places, y, strict=True)), net.initial_marking
        )
        print(f"  P-invariant {y}: {terms} = {const}")
    for x in transition_invariants(net):
        print(
            f"  T-invariant {x}: firing counts {dict(zip(net.transitions, x, strict=True))}"
        )

    print("\n-- state equation M = M0 + C.x for M = (1, 0, 2, 1), x = (2, 0)")
    c, m0, counts = net.incidence(), net.initial_marking, (2, 0)
    target = tuple(
        m0[i] + sum(c[i][j] * counts[j] for j in range(len(counts)))
        for i in range(len(m0))
    )
    print(f"  M0 + C.x = {target}, reachable: {target in graph}")


if __name__ == "__main__":
    main()
