"""Solution C4 (advanced): fixing the philosophers by resource ordering.
Statement: exercises/cpn/c4-resource-ordering.md

Fix: every philosopher picks up the lower-numbered fork first. Philosopher p uses forks
p and (p+1) mod n, so first(p) = min(p, (p+1) mod n), second(p) = max(...). Only the last
philosopher (p = n-1, forks n-1 and 0) is affected: it takes fork 0 first.

Answers:
1. Two transitions with guards express the same thing without helper functions:
   takeFirst<p> [p < n-1] takes fork p; takeFirst<p> [p = n-1] takes fork 0. Here a helper
   function in the arc expression is used instead; the unfolding is the same P/T net.
2. Naive, n = 5: 1 dead marking, shortest trace takeLeft<p=0> ... takeLeft<p=4>.
3. Ordered: no dead marking for n = 2..5, and the net is live (checked on the unfolding with
   the SCC criterion). Circular wait is impossible: forks are acquired in increasing order,
   so the philosopher holding the highest-numbered fork can always finish.
4. State counts (naive vs ordered) for n = 2..5 are printed by main(); the ordered net
   removes the deadlock and a few interleavings that led to it.
"""

from collections.abc import Callable

from petrilab.petri import analysis
from petrilab.petri.cpn import (
    CPN,
    Binding,
    ColourSet,
    FrozenMarking,
    dead_markings,
    unfold,
    var,
)
from petrilab.petri.cpn_examples import philosophers
from petrilab.petri.snakes_bridge import explore, to_snakes


def ordered_philosophers(n: int) -> CPN:
    ph = ColourSet("PH", tuple(range(n)))

    def first(b: Binding) -> list[int]:
        return [min(b["p"], (b["p"] + 1) % n)]

    def second(b: Binding) -> list[int]:
        return [max(b["p"], (b["p"] + 1) % n)]

    def both(b: Binding) -> list[int]:
        return [b["p"], (b["p"] + 1) % n]

    net = CPN(f"ordered_philosophers_{n}")
    net.add_place("Think", ph, ph.values)
    net.add_place("Fork", ph, ph.values)
    net.add_place("HasFirst", ph)
    net.add_place("Eat", ph)
    p = {"p": ph}
    net.add_transition(
        "takeFirst",
        variables=p,
        inputs={"Think": var("p"), "Fork": first},
        outputs={"HasFirst": var("p")},
    )
    net.add_transition(
        "takeSecond",
        variables=p,
        inputs={"HasFirst": var("p"), "Fork": second},
        outputs={"Eat": var("p")},
    )
    net.add_transition(
        "done",
        variables=p,
        inputs={"Eat": var("p")},
        outputs={"Think": var("p"), "Fork": both},
    )
    return net


def no_successors(net: CPN) -> Callable[[FrozenMarking], bool]:
    return lambda m: not net.successors(m)


def is_live(net: CPN) -> bool:
    pt = unfold(net)
    return analysis.is_live(explore(to_snakes(pt)), set(pt.transitions))


def check() -> None:
    naive = philosophers(5)
    assert len(dead_markings(naive.reachable())) == 1
    trace = naive.trace_to(no_successors(naive))
    assert trace == [f"takeLeft<p={i}>" for i in range(5)]

    for n in (2, 3, 4, 5):
        net = ordered_philosophers(n)
        graph = net.reachable()
        assert dead_markings(graph) == [], n
        assert net.trace_to(no_successors(net)) is None
    for n in (2, 3, 4):
        assert is_live(ordered_philosophers(n))
        assert not is_live(philosophers(n))


if __name__ == "__main__":
    check()
    for n in (2, 3, 4, 5):
        print(f"n={n}: naive {len(philosophers(n).reachable())} markings, "
              f"ordered {len(ordered_philosophers(n).reachable())} markings")  # fmt: skip
    print("C4 OK")
