"""P- and T-invariants from the incidence matrix (sympy integer nullspace)."""

import sympy

from petrilab.petri.model import Marking, PTNet


def _integer_basis(matrix: sympy.Matrix) -> list[list[int]]:
    basis = []
    for vec in matrix.nullspace():
        den = sympy.ilcm(*[sympy.fraction(x)[1] for x in vec]) if len(vec) else 1
        ints = [int(x * den) for x in vec]
        g = sympy.igcd(*ints) or 1
        basis.append([x // g for x in ints])
    return basis


def place_invariants(net: PTNet) -> list[list[int]]:
    """Basis of integer vectors ``y`` (over places) with ``y . C = 0``."""
    c = sympy.Matrix(net.incidence())
    return _integer_basis(c.T)


def transition_invariants(net: PTNet) -> list[list[int]]:
    """Basis of integer vectors ``x`` (over transitions) with ``C . x = 0``."""
    c = sympy.Matrix(net.incidence())
    return _integer_basis(c)


def is_place_invariant(net: PTNet, weights: dict[str, int]) -> bool:
    """True if the weighted token sum is preserved by every transition (``y . C = 0``)."""
    y = [weights.get(p, 0) for p in net.places]
    c = net.incidence()
    return all(
        sum(y[i] * c[i][j] for i in range(len(y))) == 0
        for j in range(len(net.transitions))
    )


def weighted_sum(net: PTNet, weights: dict[str, int], m: Marking) -> int:
    return sum(weights.get(p, 0) * n for p, n in zip(net.places, m, strict=True))
