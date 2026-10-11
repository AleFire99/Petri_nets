"""Solution P6 (advanced): the state equation is necessary, not sufficient.
Statement: exercises/petri/p6-state-equation.md

Net: t1: p1 -> p2, t2: p2 -> p1 + p3, M0 = (0, 0, 0).

Answers:
1. C = [[-1, 1], [1, -1], [0, 1]] (rows p1, p2, p3; columns t1, t2).
2. M = (0, 0, 1): M - M0 = (0, 0, 1) = C . (1, 1). x = (1, 1) >= 0 solves the state equation.
3. M0 enables nothing (every transition needs a token), so R(N, M0) = {M0}: M is NOT reachable.
   The solution x counts a cycle t1 t2 that could only run if a token were already there.
4. With M0' = (1, 0, 0): M' = (1, 0, 1) = M0' + C . (1, 1) and t1 t2 is fireable: reachable.
5. Corollary: if the state equation has no solution x >= 0, M is unreachable (cheap proof);
   if it has one, you still need exploration (or more refined conditions) to decide.
"""

import itertools

from petrilab.petri.model import Marking, PTNet


def cycle_net(m0: tuple[int, int, int] = (0, 0, 0)) -> PTNet:
    net = PTNet("cycle")
    for p, n in zip(("p1", "p2", "p3"), m0, strict=True):
        net.add_place(p, n)
    net.add_transition("t1", {"p1": 1}, {"p2": 1})
    net.add_transition("t2", {"p2": 1}, {"p1": 1, "p3": 1})
    return net


def state_equation_solutions(
    net: PTNet, target: Marking, bound: int = 5
) -> list[tuple[int, ...]]:
    """All x in {0..bound}^|T| with M0 + C.x = target (brute force: fine for tiny nets)."""
    c, m0 = net.incidence(), net.initial_marking
    sols = []
    for x in itertools.product(range(bound + 1), repeat=len(net.transitions)):
        m = tuple(
            m0[i] + sum(c[i][j] * x[j] for j in range(len(x))) for i in range(len(m0))
        )
        if m == target:
            sols.append(x)
    return sols


def check() -> None:
    net = cycle_net()
    assert net.incidence() == [[-1, 1], [1, -1], [0, 1]]
    target = (0, 0, 1)
    assert state_equation_solutions(net, target) == [(1, 1)]
    assert list(net.reachable()) == [(0, 0, 0)]
    assert net.trace_to(lambda m: m == target) is None

    marked = cycle_net((1, 0, 0))
    assert state_equation_solutions(marked, (1, 0, 1)) == [(1, 1)]
    assert marked.trace_to(lambda m: m == (1, 0, 1)) == ["t1", "t2"]

    # no solution => unreachable (the useful direction)
    assert state_equation_solutions(net, (1, 0, 0)) == []


if __name__ == "__main__":
    check()
    print(
        "P6 OK: (0, 0, 1) solves the state equation with x = (1, 1) but is unreachable"
    )
