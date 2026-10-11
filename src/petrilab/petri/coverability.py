"""Karp-Miller coverability graph for place/transition nets (docs/petri/coverability.md).

The reachability graph of an unbounded net is infinite. The coverability graph is always
finite: when a new marking ``M'`` strictly covers an ancestor ``M`` on the path from the root
(``M <= M'`` componentwise, ``M != M'``), the firing sequence from ``M`` to ``M'`` can be
repeated forever, so every place that grew is set to omega ("arbitrarily many tokens").

Exact answers it gives:
- boundedness (no omega anywhere) and, per place, the bound (or omega);
- coverability of a marking ``M`` (some reachable marking ``>= M``);
- dead transitions (a transition can fire in some reachable marking iff it labels an edge).

It does *not* answer exact reachability or deadlock freedom for unbounded nets: omega
abstracts away the precise token count. Inhibitor arcs break monotonicity (more tokens can
disable a transition), so nets with inhibitor arcs are rejected.
"""

import math
from dataclasses import dataclass, field

from petrilab.petri.model import PTNet, StateSpaceLimitError

OMEGA = math.inf
"""Token count meaning "unbounded": omega - n = omega + n = omega, omega >= n for every n."""

ExtMarking = tuple[int | float, ...]
"""Marking over the places of a PTNet; an entry is an int or OMEGA."""


@dataclass
class CoverabilityGraph:
    net: PTNet
    initial: ExtMarking
    edges: dict[ExtMarking, list[tuple[str, ExtMarking]]] = field(default_factory=dict)

    @property
    def markings(self) -> list[ExtMarking]:
        return list(self.edges)

    def __len__(self) -> int:
        return len(self.edges)

    def unbounded_places(self) -> list[str]:
        """Places that reach omega in some node, in net order."""
        names = self.net.place_names
        return [
            names[i]
            for i in range(len(names))
            if any(m[i] == OMEGA for m in self.edges)
        ]

    def is_bounded(self) -> bool:
        return not self.unbounded_places()

    def place_bound(self, place: str) -> int | float:
        """Max tokens ``place`` ever holds: an int, or OMEGA if unbounded."""
        i = self.net.place_names.index(place)
        return max(m[i] for m in self.edges)

    def is_coverable(self, target: dict[str, int]) -> bool:
        """True iff some reachable marking has at least ``target[p]`` tokens in each p."""
        idx = {p: i for i, p in enumerate(self.net.place_names)}
        unknown = set(target) - set(idx)
        if unknown:
            raise ValueError(f"unknown places {sorted(unknown)}")
        return any(all(m[idx[p]] >= n for p, n in target.items()) for m in self.edges)

    def dead_transitions(self) -> list[str]:
        """Transitions that can never fire (not live at level L1)."""
        fired = {t for succ in self.edges.values() for t, _ in succ}
        return [t for t in self.net.transitions if t not in fired]


def format_marking(m: ExtMarking) -> str:
    """``(1, ω, 0)``: readable form with omega."""
    return "(" + ", ".join("ω" if x == OMEGA else str(int(x)) for x in m) + ")"


def _enabled(net: PTNet, m: ExtMarking, t: str) -> bool:
    spec = net.transitions[t]
    idx = {p: i for i, p in enumerate(net.places)}
    return all(m[idx[p]] >= w for p, w in spec.pre.items()) and all(
        m[idx[p]] >= w for p, w in spec.read.items()
    )


def _fire(net: PTNet, m: ExtMarking, t: str) -> ExtMarking:
    spec = net.transitions[t]
    out = list(m)
    for i, p in enumerate(net.places):
        out[i] = out[i] - spec.pre.get(p, 0) + spec.post.get(p, 0)  # omega absorbs +/-
    return tuple(out)


def _covers(big: ExtMarking, small: ExtMarking) -> bool:
    return all(b >= s for b, s in zip(big, small, strict=True))


def coverability_graph(net: PTNet, max_nodes: int = 10_000) -> CoverabilityGraph:
    """Build the Karp-Miller coverability graph of ``net``.

    Nodes with equal (extended) markings are merged, which keeps the result a graph rather
    than a tree; acceleration only compares a new marking with its ancestors in the
    exploration tree, as in Karp and Miller (1969).
    """
    if any(spec.inhibit for spec in net.transitions.values()):
        raise ValueError("coverability analysis is unsound with inhibitor arcs")

    root: ExtMarking = tuple(net.initial_marking)
    graph = CoverabilityGraph(net, root)
    # exploration tree: node id -> (marking, parent id)
    tree: list[tuple[ExtMarking, int | None]] = [(root, None)]
    stack = [0]
    while stack:
        node = stack.pop()
        m, _ = tree[node]
        if m in graph.edges:  # same marking already expanded elsewhere: merge
            continue
        succ: list[tuple[str, ExtMarking]] = []
        for t in net.transitions:
            if not _enabled(net, m, t):
                continue
            nxt = _fire(net, m, t)
            # acceleration: walk the ancestors of the new node (including ``node`` itself)
            anc: int | None = node
            while anc is not None:
                a, anc_parent = tree[anc]
                if a != nxt and _covers(nxt, a):
                    nxt = tuple(
                        OMEGA if x > y else x for x, y in zip(nxt, a, strict=True)
                    )
                anc = anc_parent
            succ.append((t, nxt))
            if nxt not in graph.edges:
                if len(tree) >= max_nodes:
                    raise StateSpaceLimitError(f"more than {max_nodes} tree nodes")
                tree.append((nxt, node))
                stack.append(len(tree) - 1)
        graph.edges[m] = succ
    # a marking pushed twice is expanded once; every edge target is a key
    return graph
