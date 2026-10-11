"""Reachability, deadlocks and liveness: dining philosophers and mutex (docs/petri/examples.md).

Run: uv run python examples/reachability_deadlock.py
"""

from collections.abc import Callable

from petrilab.petri import analysis, examples
from petrilab.petri.model import Marking, PTNet
from petrilab.petri.snakes_bridge import explore, to_snakes


def dead_in(net: PTNet) -> Callable[[Marking], bool]:
    """Predicate: no transition of ``net`` is enabled."""
    return lambda m: not net.enabled_transitions(m)


def main() -> None:
    print("-- dining philosophers, n = 3")
    for atomic in (False, True):
        net = examples.dining_philosophers(3, atomic=atomic)
        graph = net.reachable()
        dead = [m for m, succ in graph.items() if not succ]
        space = explore(to_snakes(net))
        live = analysis.is_live(space, set(net.transitions))
        print(f"  {net.name}: {len(graph)} markings, {len(dead)} dead, live={live}")
        if dead:
            trace = net.trace_to(dead_in(net))
            print(f"    shortest trace to deadlock: {trace}")
            held = {p: n for p, n in net.marking_dict(dead[0]).items() if n}
            print(f"    dead marking: {held}")

    print("\n-- mutex: safety (never both in Crit) and liveness")
    net = examples.mutex()
    graph = net.reachable()
    both = [
        m
        for m in graph
        if net.marking_dict(m)["Crit1"] and net.marking_dict(m)["Crit2"]
    ]
    space = explore(to_snakes(net))
    print(
        f"  {len(graph)} markings, both critical: {len(both)}, safe(1-bounded): {analysis.is_safe(space)}"
    )
    print(
        f"  deadlock-free: {analysis.is_deadlock_free(space)}, live: {analysis.is_live(space, set(net.transitions))}"
    )
    print(
        f"  trace to Crit2: {net.trace_to(lambda m: net.marking_dict(m)['Crit2'] == 1)}"
    )


if __name__ == "__main__":
    main()
