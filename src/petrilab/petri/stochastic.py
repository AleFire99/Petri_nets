"""Stochastic Petri net: CTMC steady state from the reachability graph (docs/petri/stochastic.md)."""

import numpy as np

from petrilab.petri.model import Marking, PTNet


def steady_state(net: PTNet, max_states: int = 10_000) -> dict[Marking, float]:
    """Solve ``pi Q = 0, sum(pi) = 1`` with single-server exponential transitions."""
    graph = net.reachable(max_states)
    states = list(graph)
    index = {m: i for i, m in enumerate(states)}
    q = np.zeros((len(states), len(states)))
    for m, succ in graph.items():
        for t, nxt in succ:
            rate = net.transitions[t].rate
            if rate is None:
                raise ValueError(f"transition {t!r} has no rate")
            if nxt != m:
                q[index[m], index[nxt]] += rate
        q[index[m], index[m]] = -q[index[m]].sum()
    a = np.vstack([q.T, np.ones(len(states))])
    b = np.zeros(len(states) + 1)
    b[-1] = 1.0
    pi, *_ = np.linalg.lstsq(a, b, rcond=None)
    return {m: float(pi[index[m]]) for m in states}


def expected_tokens(net: PTNet, pi: dict[Marking, float], place: str) -> float:
    i = net.place_names.index(place)
    return sum(p * m[i] for m, p in pi.items())


def throughput(net: PTNet, pi: dict[Marking, float], transition: str) -> float:
    rate = net.transitions[transition].rate
    assert rate is not None
    return rate * sum(p for m, p in pi.items() if net.enabled(m, transition))


def mm1k(arrival: float = 1.0, service: float = 2.0, capacity: int = 3) -> PTNet:
    n = PTNet("mm1k")
    n.add_place("Free", capacity)
    n.add_place("Queue")
    n.add_transition("arrive", {"Free": 1}, {"Queue": 1}, rate=arrival)
    n.add_transition("serve", {"Queue": 1}, {"Free": 1}, rate=service)
    return n
