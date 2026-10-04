"""Behavioural properties over a reachability graph (works for any SNAKES net)."""

from collections.abc import Callable

import networkx as nx

from petrilab.petri.snakes_bridge import MarkingKey, StateSpace


def dead_markings(space: StateSpace) -> list[MarkingKey]:
    """Reachable markings with no enabled transition."""
    return [n for n in space.graph if space.graph.out_degree(n) == 0]


def is_deadlock_free(space: StateSpace) -> bool:
    return not dead_markings(space)


def fired_transitions(space: StateSpace) -> set[str]:
    return {d["transition"] for _, _, d in space.graph.edges(data=True)}


def max_tokens(space: StateSpace, place: str) -> int:
    return max(space.tokens(k, place) for k in space.graph)


def is_bounded(space: StateSpace) -> bool:
    """Bounded iff exploration finished without hitting the token cap."""
    return not space.exceeded_cap


def is_safe(space: StateSpace) -> bool:
    """1-safe: no place ever holds more than one token."""
    return all(space.tokens(k, p) <= 1 for k in space.graph for p in space.markings[k])


def is_live(space: StateSpace, all_transitions: set[str]) -> bool:
    """Live (L4): from every reachable marking every transition can still fire.

    On a finite graph this holds iff every terminal strongly connected component contains an edge
    for every transition.
    """
    cond = nx.condensation(space.graph)
    for scc_id in cond:
        if cond.out_degree(scc_id) != 0:
            continue
        members = cond.nodes[scc_id]["members"]
        used = {
            d["transition"]
            for u, v, d in space.graph.out_edges(members, data=True)
            if v in members and u in members
        }
        if used != all_transitions:
            return False
    return True


def can_reach(
    space: StateSpace, predicate: Callable[[StateSpace, MarkingKey], bool]
) -> bool:
    return any(predicate(space, k) for k in space.graph)
