"""Workflow-net checks and soundness (petri/docs/workflow.md)."""

from typing import TYPE_CHECKING

import networkx as nx

from petrilab.petri.model import PTNet, StateSpaceLimitError

if TYPE_CHECKING:
    from pm4py.objects.petri_net.obj import Marking as PmMarking
    from pm4py.objects.petri_net.obj import PetriNet as PmNet


def is_workflow_net(net: PTNet, source: str = "i", sink: str = "o") -> bool:
    """One source place, one sink place, and every node on a path from source to sink."""
    g: nx.DiGraph[tuple[str, str]] = nx.DiGraph()
    for t, spec in net.transitions.items():
        for p in spec.pre:
            g.add_edge(("p", p), ("t", t))
        for p in spec.post:
            g.add_edge(("t", t), ("p", p))
    for p in net.places:
        g.add_node(("p", p))
    for t in net.transitions:
        g.add_node(("t", t))
    s, k = ("p", source), ("p", sink)
    if g.in_degree(s) != 0 or g.out_degree(k) != 0:
        return False
    reach_from_s = nx.descendants(g, s) | {s}
    reach_to_k = nx.ancestors(g, k) | {k}
    return all(n in reach_from_s and n in reach_to_k for n in g)


def initial_workflow_marking(net: PTNet, source: str = "i") -> PTNet:
    """Return ``net`` with exactly one token in the source place and none elsewhere."""
    for p in net.places:
        net.places[p] = 1 if p == source else 0
    return net


def is_sound(
    net: PTNet, source: str = "i", sink: str = "o", max_states: int = 50_000
) -> bool:
    """Classical soundness, decided on the reachability graph (the net must be bounded)."""
    if not is_workflow_net(net, source, sink):
        return False
    initial_workflow_marking(net, source)
    try:
        graph = net.reachable(max_states)
    except StateSpaceLimitError:
        return False
    final = net.marking(**{sink: 1})
    if final not in graph:
        return False
    rev: nx.DiGraph[tuple[int, ...]] = nx.DiGraph()
    rev.add_nodes_from(graph)
    for m, succ in graph.items():
        for _, nxt in succ:
            rev.add_edge(nxt, m)
    can_complete = nx.descendants(rev, final) | {final}  # markings that can reach final
    if len(can_complete) != len(graph):
        return False  # option to complete violated
    k = net.place_names.index(sink)
    if any(m[k] > 0 and m != final for m in graph):
        return False  # proper completion violated
    fired = {t for succ in graph.values() for t, _ in succ}
    return fired == set(net.transitions)  # no dead transitions


def to_pm4py(
    net: PTNet, source: str = "i", sink: str = "o"
) -> "tuple[PmNet, PmMarking, PmMarking]":
    """Needs the optional ``soundness`` extra (PM4Py, AGPL v3)."""
    try:
        from pm4py.objects.petri_net.obj import Marking as PmMarking
        from pm4py.objects.petri_net.obj import PetriNet as PmNet
        from pm4py.objects.petri_net.utils import petri_utils
    except ImportError as exc:
        raise ImportError(
            "PM4Py is not installed (AGPL v3, optional): pip install 'petrilab[soundness]'"
        ) from exc
    pm = PmNet(net.name)
    places = {p: PmNet.Place(p) for p in net.places}
    pm.places.update(places.values())
    for t, spec in net.transitions.items():
        tr = PmNet.Transition(t, t)
        pm.transitions.add(tr)
        for p, w in spec.pre.items():
            petri_utils.add_arc_from_to(places[p], tr, pm, weight=w)
        for p, w in spec.post.items():
            petri_utils.add_arc_from_to(tr, places[p], pm, weight=w)
    return pm, PmMarking({places[source]: 1}), PmMarking({places[sink]: 1})


def is_sound_pm4py(net: PTNet, source: str = "i", sink: str = "o") -> bool:
    from pm4py.algo.analysis.woflan import algorithm as woflan

    pm, im, fm = to_pm4py(net, source, sink)
    return bool(
        woflan.apply(pm, im, fm, parameters={"return_asap_when_not_sound": True})
    )


def parallel_review() -> PTNet:
    n = PTNet("parallel_review")
    for p in ("i", "a", "b", "a2", "b2", "o"):
        n.add_place(p, 1 if p == "i" else 0)
    n.add_transition("register", {"i": 1}, {"a": 1, "b": 1})
    n.add_transition("checkA", {"a": 1}, {"a2": 1})
    n.add_transition("checkB", {"b": 1}, {"b2": 1})
    n.add_transition("decide", {"a2": 1, "b2": 1}, {"o": 1})
    return n


def xor_and_mismatch() -> PTNet:
    n = PTNet("xor_and_mismatch")
    for p in ("i", "pa", "pb", "o"):
        n.add_place(p, 1 if p == "i" else 0)
    n.add_transition("chooseA", {"i": 1}, {"pa": 1})
    n.add_transition("chooseB", {"i": 1}, {"pb": 1})
    n.add_transition("join", {"pa": 1, "pb": 1}, {"o": 1})
    return n
