"""Solution P4 (intermediate): proving mutual exclusion with P-invariants.
Statement: exercises/petri/p4-mutex-invariants.md

Answers:
1. sympy returns a basis with negative entries (a basis is not unique).
2. Semi-positive invariants (all weights >= 0):
     y1 = Idle1 + Wait1 + Crit1 = 1      (process 1 is in exactly one local state)
     y2 = Idle2 + Wait2 + Crit2 = 1
     y3 = Mutex + Crit1 + Crit2 = 1      (the lock is free or held by one process)
   Each is a combination of the basis vectors, and each satisfies y . C = 0.
3. From y3 and M >= 0: Crit1 + Crit2 = 1 - Mutex <= 1, in *every* reachable marking, for any
   number of steps. No state-space exploration needed: the proof is structural.
4. T-invariants (request_k, enter_k, leave_k) = 1: one full cycle of process k.
5. The invariant argument survives adding more processes (exercise C2 / cpn_examples.mutex).
"""

from petrilab.petri import examples
from petrilab.petri.invariants import (
    is_place_invariant,
    place_invariants,
    transition_invariants,
    weighted_sum,
)

Y1 = {"Idle1": 1, "Wait1": 1, "Crit1": 1}
Y2 = {"Idle2": 1, "Wait2": 1, "Crit2": 1}
Y3 = {"Mutex": 1, "Crit1": 1, "Crit2": 1}


def check() -> None:
    net = examples.mutex()
    basis = place_invariants(net)
    assert len(basis) == 3
    assert any(min(v) < 0 for v in basis)  # answer 1: basis has negative entries

    for y in (Y1, Y2, Y3):
        assert is_place_invariant(net, y)
        assert weighted_sum(net, y, net.initial_marking) == 1
        # sanity check against the reachability graph
        assert all(weighted_sum(net, y, m) == 1 for m in net.reachable())

    # Y3 lies in the span of the basis: solve basis^T a = y3 over the rationals
    import sympy

    b = sympy.Matrix(basis).T
    y3 = sympy.Matrix([Y3.get(p, 0) for p in net.places])
    sol, params = b.gauss_jordan_solve(y3)
    assert not params  # unique combination
    assert b * sol == y3

    # mutual exclusion follows from Y3
    assert all(
        net.marking_dict(m)["Crit1"] + net.marking_dict(m)["Crit2"] <= 1
        for m in net.reachable()
    )

    tinv = transition_invariants(net)
    names = list(net.transitions)
    cycles = sorted(sorted(names[i] for i, x in enumerate(v) if x) for v in tinv)
    assert cycles == [
        ["enter1", "leave1", "request1"],
        ["enter2", "leave2", "request2"],
    ]

    # invalid candidate: Wait1 + Crit1 is not invariant (request1 adds a token)
    assert not is_place_invariant(net, {"Wait1": 1, "Crit1": 1})


if __name__ == "__main__":
    check()
    print("P4 OK: Mutex + Crit1 + Crit2 = 1 is a P-invariant")
