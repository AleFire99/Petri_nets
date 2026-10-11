"""Coloured Petri nets: bindings, firing, reachability, unfolding (docs/petri/cpn-formal.md).

Run: uv run python examples/cpn_bindings_and_unfolding.py
"""

from petrilab.petri import analysis, cpn_examples, examples
from petrilab.petri.colored import jobs_net
from petrilab.petri.cpn import NotEnabledError, dead_markings, format_marking, unfold
from petrilab.petri.snakes_bridge import explore


def main() -> None:
    print("-- jobs net: guard n > 1")
    net = cpn_examples.jobs()
    m0 = net.initial_marking
    print(f"  M0: {format_marking(m0)}")
    print(f"  all bindings of square: {len(net.all_bindings('square'))} (n in 0..9)")
    print(f"  enabled in M0: {net.enabled_bindings(m0, 'square')}")
    try:
        net.fire(m0, "square", {"n": 1})
    except NotEnabledError as exc:
        print(f"  fire square<n=1>: NotEnabledError: {exc}")
    graph = net.reachable()
    for m, succ in graph.items():
        print(f"  {format_marking(m)} -> {[label for label, _ in succ]}")
    print(f"  dead: {[format_marking(m) for m in dead_markings(graph)]}")
    snakes = explore(jobs_net())
    print(
        f"  SNAKES agrees: {len(snakes)} markings, {len(analysis.dead_markings(snakes))} dead"
    )

    print("\n-- philosophers folded (n = 3)")
    phil = cpn_examples.philosophers(3)
    m0 = phil.initial_marking
    m1 = phil.fire(m0, "takeLeft", {"p": 1})
    print(f"  M0: {format_marking(m0)}")
    print(f"  takeLeft<p=1>: {format_marking(m1)}")
    print(f"  enabled takeRight: {phil.enabled_bindings(m1, 'takeRight')}")
    graph = phil.reachable()
    pt_graph = examples.dining_philosophers(3).reachable()
    print(f"  CPN: {len(graph)} markings, P/T: {len(pt_graph)} markings")
    print(f"  deadlock trace: {phil.trace_to(lambda m: not phil.successors(m))}")

    print("\n-- unfolding")
    pt = unfold(phil)
    print(f"  {len(phil.places)} CPN places -> {len(pt.places)} P/T places")
    print(
        f"  {len(phil.transitions)} CPN transitions -> {len(pt.transitions)} P/T transitions"
    )
    print(f"  takeRight<p=2> pre: {pt.transitions['takeRight<p=2>'].pre}")
    print(f"  unfolded reachability: {len(pt.reachable())} markings")


if __name__ == "__main__":
    main()
