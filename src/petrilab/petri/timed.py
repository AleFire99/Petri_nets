"""Time Petri net explorer with integer-time semantics (petri/docs/timed.md).

A transition with interval ``(eft, lft)`` may fire when it has been continuously enabled for ``c``
time units with ``eft <= c <= lft``, and time cannot advance past ``lft`` while it is enabled.
"""

from collections import deque
from dataclasses import dataclass

from petrilab.petri.model import Marking, PTNet, StateSpaceLimitError

Clocks = tuple[
    tuple[str, int], ...
]  # sorted (transition, time enabled) for enabled transitions
TimedState = tuple[Marking, Clocks]


@dataclass
class TimedSpace:
    states: set[TimedState]
    fired: set[str]
    edges: dict[TimedState, list[tuple[str, TimedState]]]

    @property
    def markings(self) -> set[Marking]:
        return {m for m, _ in self.states}


def _interval(net: PTNet, t: str) -> tuple[int, int | None]:
    return net.transitions[t].interval or (0, None)


def _clock_cap(net: PTNet, t: str) -> int:
    eft, lft = _interval(net, t)
    return eft if lft is None else lft


def initial_state(net: PTNet) -> TimedState:
    m = net.initial_marking
    return m, tuple(sorted((t, 0) for t in net.enabled_transitions(m)))


def timed_successors(net: PTNet, state: TimedState) -> list[tuple[str, TimedState]]:
    """Fire edges are labelled with the transition name, time steps with ``"tick"``."""
    m, clocks = state
    cdict = dict(clocks)
    out: list[tuple[str, TimedState]] = []
    for t, c in cdict.items():
        eft, lft = _interval(net, t)
        if c >= eft and (lft is None or c <= lft):
            spec = net.transitions[t]
            mid = list(m)
            names = net.place_names
            for p, w in spec.pre.items():
                mid[names.index(p)] -= w
            new_m = net.fire(m, t)
            persistent = {
                u
                for u in cdict
                if u != t and _enabled_in(net, tuple(mid), u) and net.enabled(new_m, u)
            }
            new_clocks = {u: cdict[u] for u in persistent}
            for u in net.enabled_transitions(new_m):
                new_clocks.setdefault(u, 0)
            out.append((t, (new_m, tuple(sorted(new_clocks.items())))))
    urgent = any(
        (lft := _interval(net, t)[1]) is not None and c >= lft for t, c in cdict.items()
    )
    if cdict and not urgent:
        ticked = tuple(
            sorted((t, min(c + 1, _clock_cap(net, t))) for t, c in cdict.items())
        )
        if ticked != clocks:
            out.append(("tick", (m, ticked)))
    return out


def _enabled_in(net: PTNet, m: tuple[int, ...], t: str) -> bool:
    """Enabledness of ``t`` in an intermediate marking (may have consumed tokens)."""
    return net.enabled(m, t)


def explore_timed(net: PTNet, max_states: int = 100_000) -> TimedSpace:
    start = initial_state(net)
    states = {start}
    edges: dict[TimedState, list[tuple[str, TimedState]]] = {}
    fired: set[str] = set()
    queue = deque([start])
    while queue:
        s = queue.popleft()
        edges[s] = timed_successors(net, s)
        for label, nxt in edges[s]:
            if label != "tick":
                fired.add(label)
            if nxt not in states:
                if len(states) >= max_states:
                    raise StateSpaceLimitError(f"more than {max_states} timed states")
                states.add(nxt)
                queue.append(nxt)
    return TimedSpace(states, fired, edges)
