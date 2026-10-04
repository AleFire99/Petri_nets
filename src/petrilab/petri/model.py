"""A small place/transition net spec: single source of truth for the Petri designs.

Supports weighted arcs, inhibitor arcs, read (test) arcs, and optional timing/rate annotations.
Markings are tuples of ints ordered like ``PTNet.places``.
"""

from collections import deque
from dataclasses import dataclass, field

Marking = tuple[int, ...]


@dataclass
class TransitionSpec:
    name: str
    pre: dict[str, int] = field(default_factory=dict)
    post: dict[str, int] = field(default_factory=dict)
    inhibit: dict[str, int] = field(default_factory=dict)
    read: dict[str, int] = field(default_factory=dict)
    interval: tuple[int, int | None] | None = (
        None  # (earliest, latest) firing time; None = inf
    )
    rate: float | None = None  # exponential firing rate


class StateSpaceLimitError(RuntimeError):
    """Raised when exploration exceeds the allowed number of states."""


@dataclass
class PTNet:
    name: str
    places: dict[str, int] = field(default_factory=dict)  # place -> initial tokens
    transitions: dict[str, TransitionSpec] = field(default_factory=dict)

    def add_place(self, name: str, tokens: int = 0) -> None:
        if name in self.places:
            raise ValueError(f"duplicate place {name!r}")
        self.places[name] = tokens

    def add_transition(
        self,
        name: str,
        pre: dict[str, int] | None = None,
        post: dict[str, int] | None = None,
        *,
        inhibit: dict[str, int] | None = None,
        read: dict[str, int] | None = None,
        interval: tuple[int, int | None] | None = None,
        rate: float | None = None,
    ) -> None:
        if name in self.transitions:
            raise ValueError(f"duplicate transition {name!r}")
        spec = TransitionSpec(
            name, dict(pre or {}), dict(post or {}), dict(inhibit or {}), dict(read or {}),
            interval, rate,
        )  # fmt: skip
        for arcs in (spec.pre, spec.post, spec.inhibit, spec.read):
            unknown = set(arcs) - set(self.places)
            if unknown:
                raise ValueError(
                    f"unknown places {sorted(unknown)} in transition {name!r}"
                )
        self.transitions[name] = spec

    # -- markings ---------------------------------------------------------------------------
    @property
    def place_names(self) -> list[str]:
        return list(self.places)

    @property
    def initial_marking(self) -> Marking:
        return tuple(self.places.values())

    def marking_dict(self, m: Marking) -> dict[str, int]:
        return dict(zip(self.places, m, strict=True))

    def marking(self, **tokens: int) -> Marking:
        """Marking with the given places set (others zero)."""
        unknown = set(tokens) - set(self.places)
        if unknown:
            raise ValueError(f"unknown places {sorted(unknown)}")
        return tuple(tokens.get(p, 0) for p in self.places)

    # -- firing -----------------------------------------------------------------------------
    def enabled(self, m: Marking, t: str) -> bool:
        spec = self.transitions[t]
        d = self.marking_dict(m)
        return (
            all(d[p] >= w for p, w in spec.pre.items())
            and all(d[p] >= w for p, w in spec.read.items())
            and all(d[p] < w for p, w in spec.inhibit.items())
        )

    def enabled_transitions(self, m: Marking) -> list[str]:
        return [t for t in self.transitions if self.enabled(m, t)]

    def fire(self, m: Marking, t: str) -> Marking:
        if not self.enabled(m, t):
            raise ValueError(f"transition {t!r} not enabled in {self.marking_dict(m)}")
        spec = self.transitions[t]
        d = self.marking_dict(m)
        for p, w in spec.pre.items():
            d[p] -= w
        for p, w in spec.post.items():
            d[p] += w
        return tuple(d[p] for p in self.places)

    def successors(self, m: Marking) -> list[tuple[str, Marking]]:
        return [(t, self.fire(m, t)) for t in self.enabled_transitions(m)]

    def reachable(
        self, max_states: int = 100_000
    ) -> dict[Marking, list[tuple[str, Marking]]]:
        """Reachability graph as adjacency lists; raises if it exceeds ``max_states``."""
        start = self.initial_marking
        graph: dict[Marking, list[tuple[str, Marking]]] = {}
        queue = deque([start])
        seen = {start}
        while queue:
            m = queue.popleft()
            graph[m] = self.successors(m)
            for _, nxt in graph[m]:
                if nxt not in seen:
                    if len(seen) >= max_states:
                        raise StateSpaceLimitError(f"more than {max_states} states")
                    seen.add(nxt)
                    queue.append(nxt)
        return graph

    # -- structure --------------------------------------------------------------------------
    def incidence(self) -> list[list[int]]:
        """Incidence matrix C[place][transition] = post - pre (read/inhibitor arcs ignored)."""
        return [
            [
                self.transitions[t].post.get(p, 0) - self.transitions[t].pre.get(p, 0)
                for t in self.transitions
            ]
            for p in self.places
        ]
