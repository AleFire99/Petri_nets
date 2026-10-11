"""Solution C3 (intermediate): invariants of a CPN via its unfolding.
Statement: exercises/cpn/c3-unfolding-invariants.md

Answers (n = 3 naive philosophers):
1. Unfolding: 4 places x 3 colours = 12 P/T places; 3 transitions x 3 bindings = 9.
2. Philosopher invariants, for each p: Think[p] + HasLeft[p] + Eat[p] = 1.
3. Fork invariants, for each fork f:
     Fork[f] + HasLeft[f] + Eat[f] + Eat[(f - 1) mod n] = 1
   fork f is on the table, held as the left fork of philosopher f, or in use by an eating
   philosopher (f eats with forks f and f+1; f-1 eats with forks f-1 and f).
4. Together these 2n invariants span the whole P-invariant space (rank 2n = 6).
5. Corollary: Eat[p] + Eat[p+1] <= 1 (from the fork invariant for f = p+1): neighbours never
   eat together. The deadlock is still invisible to the invariants (see P3).
"""

from petrilab.petri.cpn import unfold
from petrilab.petri.cpn_examples import philosophers
from petrilab.petri.invariants import is_place_invariant, place_invariants, weighted_sum
from petrilab.petri.model import PTNet


def philosopher_invariant(p: int) -> dict[str, int]:
    return {f"Think[{p}]": 1, f"HasLeft[{p}]": 1, f"Eat[{p}]": 1}


def fork_invariant(f: int, n: int) -> dict[str, int]:
    return {
        f"Fork[{f}]": 1,
        f"HasLeft[{f}]": 1,
        f"Eat[{f}]": 1,
        f"Eat[{(f - 1) % n}]": 1,
    }


def unfolded(n: int = 3) -> PTNet:
    return unfold(philosophers(n))


def check() -> None:
    for n in (2, 3, 4):
        pt = unfolded(n)
        assert len(pt.places) == 4 * n and len(pt.transitions) == 3 * n
        invariants = [philosopher_invariant(p) for p in range(n)] + [
            fork_invariant(f, n) for f in range(n)
        ]
        for y in invariants:
            assert is_place_invariant(pt, y), y
            assert weighted_sum(pt, y, pt.initial_marking) == 1
        assert len(place_invariants(pt)) == 2 * n  # answer 4: dimension of the space
        for m in pt.reachable():
            d = pt.marking_dict(m)
            assert all(d[f"Eat[{p}]"] + d[f"Eat[{(p + 1) % n}]"] <= 1 for p in range(n))


if __name__ == "__main__":
    check()
    print("C3 OK:", fork_invariant(0, 3))
