"""A small, hand-written coloured Petri net (CPN) engine (docs/petri/cpn-formal.md).

Follows Jensen's definition with finite colour sets:

- a **colour set** is a finite set of values (ints, strings, tuples: anything hashable);
- a **place** has a colour set and holds a *multiset* of tokens of that colour set;
- a **transition** declares typed variables, an optional guard, and arc expressions;
- an **arc expression** maps a binding (variable -> value) to a multiset of tokens;
- a **binding element** ``(t, b)`` is enabled in ``M`` iff the guard holds and every input
  place holds at least the multiset its arc expression evaluates to.

Bindings are found by enumerating the cartesian product of the variable domains. That is
exponential in the number of variables but transparent, which is the point here; SNAKES
(``colored.py``) does pattern matching instead and is the cross-check.

``unfold`` translates a CPN into an equivalent ``PTNet`` (one place per (place, colour),
one transition per enabled-by-guard binding), so every P/T analysis in this package
(reachability, invariants, coverability) also applies to CPNs.
"""

import itertools
from collections import Counter, deque
from collections.abc import Callable, Hashable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any

from petrilab.petri.model import PTNet, StateSpaceLimitError

Colour = Hashable
Binding = Mapping[str, Any]
"""Variable -> value. Values are colours; typed Any so arc expressions can do arithmetic."""
Multiset = Counter[Colour]
ArcExpr = Callable[[Binding], Iterable[Colour]]
"""Arc inscription: binding -> tokens (repeat a token for multiplicity)."""
Guard = Callable[[Binding], bool]

FrozenMarking = tuple[tuple[str, tuple[tuple[Colour, int], ...]], ...]
"""Hashable marking: ((place, ((colour, count), ...)), ...), sorted for canonical form."""


class ColourError(TypeError):
    """A token does not belong to the colour set of its place."""


class NotEnabledError(ValueError):
    """Firing a binding element that is not enabled."""


@dataclass(frozen=True)
class ColourSet:
    name: str
    values: tuple[Colour, ...]

    def __contains__(self, c: object) -> bool:
        return c in self.values

    def __iter__(self) -> Iterator[Colour]:
        return iter(self.values)


UNIT = ColourSet("UNIT", ((),))
"""The colour set with a single value ``()``: plain black tokens."""


def var(name: str) -> ArcExpr:
    """Arc expression ``name``: one token, the value bound to the variable."""
    return lambda b: [b[name]]


def const(*tokens: Colour) -> ArcExpr:
    """Arc expression with fixed tokens, e.g. ``const(())`` for one black token."""
    return lambda b: list(tokens)


@dataclass
class CPNPlace:
    name: str
    colour_set: ColourSet
    initial: Multiset


@dataclass
class CPNTransition:
    name: str
    variables: dict[str, ColourSet]
    guard: Guard | None
    inputs: dict[str, ArcExpr]
    outputs: dict[str, ArcExpr]


def binding_label(t: str, b: Binding) -> str:
    """``take<p=1>``: transition name plus its binding, variables sorted."""
    if not b:
        return t
    return f"{t}<{', '.join(f'{k}={b[k]!r}' for k in sorted(b))}>"


def _key(c: Colour) -> tuple[str, str]:
    # tokens of different types cannot be compared directly; sort by type then repr
    return (type(c).__name__, repr(c))


@dataclass
class CPN:
    name: str
    places: dict[str, CPNPlace] = field(default_factory=dict)
    transitions: dict[str, CPNTransition] = field(default_factory=dict)

    # -- construction -----------------------------------------------------------------------
    def add_place(
        self, name: str, colour_set: ColourSet, initial: Iterable[Colour] = ()
    ) -> None:
        if name in self.places:
            raise ValueError(f"duplicate place {name!r}")
        tokens = Counter(initial)
        bad = [c for c in tokens if c not in colour_set]
        if bad:
            raise ColourError(
                f"{bad!r} not in colour set {colour_set.name} of {name!r}"
            )
        self.places[name] = CPNPlace(name, colour_set, tokens)

    def add_transition(
        self,
        name: str,
        *,
        variables: Mapping[str, ColourSet] | None = None,
        guard: Guard | None = None,
        inputs: Mapping[str, ArcExpr] | None = None,
        outputs: Mapping[str, ArcExpr] | None = None,
    ) -> None:
        if name in self.transitions:
            raise ValueError(f"duplicate transition {name!r}")
        ins, outs = dict(inputs or {}), dict(outputs or {})
        unknown = (set(ins) | set(outs)) - set(self.places)
        if unknown:
            raise ValueError(f"unknown places {sorted(unknown)} in transition {name!r}")
        self.transitions[name] = CPNTransition(
            name, dict(variables or {}), guard, ins, outs
        )

    # -- markings ---------------------------------------------------------------------------
    @staticmethod
    def freeze(m: Mapping[str, Multiset]) -> FrozenMarking:
        return tuple(
            (p, tuple(sorted(((c, n) for c, n in m[p].items() if n > 0), key=lambda x: _key(x[0]))))
            for p in sorted(m)
        )  # fmt: skip

    @staticmethod
    def thaw(m: FrozenMarking) -> dict[str, Multiset]:
        return {p: Counter(dict(items)) for p, items in m}

    @property
    def initial_marking(self) -> FrozenMarking:
        return self.freeze({p: pl.initial for p, pl in self.places.items()})

    @staticmethod
    def tokens(m: FrozenMarking, place: str) -> Multiset:
        """Multiset of tokens in ``place`` (empty Counter if none)."""
        for p, items in m:
            if p == place:
                return Counter(dict(items))
        raise KeyError(place)

    # -- firing rule ------------------------------------------------------------------------
    def all_bindings(self, t: str) -> list[dict[str, Any]]:
        """Every assignment of the transition's variables (guard not yet applied)."""
        tr = self.transitions[t]
        names = sorted(tr.variables)
        domains = [tr.variables[v].values for v in names]
        return [
            dict(zip(names, vals, strict=True)) for vals in itertools.product(*domains)
        ]

    def _arc(self, expr: ArcExpr, b: Binding, place: str) -> Multiset:
        ms = Counter(expr(b))
        bad = [c for c in ms if c not in self.places[place].colour_set]
        if bad:
            cs = self.places[place].colour_set.name
            raise ColourError(f"arc to/from {place!r} produced {bad!r}, not in {cs}")
        return ms

    def is_enabled(self, m: FrozenMarking, t: str, b: Binding) -> bool:
        tr = self.transitions[t]
        if tr.guard is not None and not tr.guard(b):
            return False
        current = self.thaw(m)
        for p, expr in tr.inputs.items():
            need = self._arc(expr, b, p)
            have = current.get(p, Counter())
            if any(have[c] < n for c, n in need.items()):
                return False
        return True

    def enabled_bindings(self, m: FrozenMarking, t: str) -> list[dict[str, Any]]:
        return [b for b in self.all_bindings(t) if self.is_enabled(m, t, b)]

    def fire(self, m: FrozenMarking, t: str, b: Binding) -> FrozenMarking:
        """Occurrence of binding element ``(t, b)``: M' = M - E(in)<b> + E(out)<b>."""
        if t not in self.transitions:
            raise KeyError(f"unknown transition {t!r}")
        tr = self.transitions[t]
        missing = set(tr.variables) - set(b)
        if missing:
            raise NotEnabledError(
                f"binding for {t!r} misses variables {sorted(missing)}"
            )
        if not self.is_enabled(m, t, b):
            raise NotEnabledError(f"{binding_label(t, b)} not enabled")
        nxt = self.thaw(m)
        for p, expr in tr.inputs.items():
            nxt[p] = nxt[p] - self._arc(expr, b, p)
        for p, expr in tr.outputs.items():
            nxt[p] = nxt[p] + self._arc(expr, b, p)
        return self.freeze(nxt)

    def successors(self, m: FrozenMarking) -> list[tuple[str, FrozenMarking]]:
        """(binding label, next marking) for every enabled binding element."""
        return [
            (binding_label(t, b), self.fire(m, t, b))
            for t in self.transitions
            for b in self.enabled_bindings(m, t)
        ]

    def reachable(
        self, max_states: int = 100_000
    ) -> dict[FrozenMarking, list[tuple[str, FrozenMarking]]]:
        """Reachability (occurrence) graph as adjacency lists, breadth-first."""
        start = self.initial_marking
        graph: dict[FrozenMarking, list[tuple[str, FrozenMarking]]] = {}
        seen = {start}
        queue = deque([start])
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

    def trace_to(
        self, target: Callable[[FrozenMarking], bool], max_states: int = 100_000
    ) -> list[str] | None:
        """Shortest sequence of binding labels to a marking satisfying ``target``."""
        start = self.initial_marking
        parent: dict[FrozenMarking, tuple[FrozenMarking, str] | None] = {start: None}
        queue = deque([start])
        while queue:
            m = queue.popleft()
            if target(m):
                trace: list[str] = []
                step = parent[m]
                while step is not None:
                    m, label = step
                    trace.append(label)
                    step = parent[m]
                return trace[::-1]
            for label, nxt in self.successors(m):
                if nxt not in parent:
                    if len(parent) >= max_states:
                        raise StateSpaceLimitError(f"more than {max_states} states")
                    parent[nxt] = (m, label)
                    queue.append(nxt)
        return None


def dead_markings(
    graph: Mapping[FrozenMarking, list[tuple[str, FrozenMarking]]],
) -> list[FrozenMarking]:
    return [m for m, succ in graph.items() if not succ]


def format_marking(m: FrozenMarking) -> str:
    """``Jobs={1, 3} Results={4}``; multiplicity > 1 in CPN Tools style: ``2`'a'``."""

    def ms(items: tuple[tuple[Colour, int], ...]) -> str:
        return (
            "{" + ", ".join(f"{n}`{c!r}" if n > 1 else repr(c) for c, n in items) + "}"
        )

    return " ".join(f"{p}={ms(items)}" for p, items in m)


# -- unfolding ------------------------------------------------------------------------------
def unfolded_place(place: str, colour: Colour) -> str:
    """Name of the P/T place for ``colour`` in ``place``, e.g. ``Fork[1]``."""
    return f"{place}[{colour!r}]" if colour != () else place


def unfold(cpn: CPN) -> PTNet:
    """Equivalent place/transition net.

    One P/T place per (place, colour), one P/T transition per binding that satisfies the
    guard. The reachability graphs are isomorphic: every CPN marking maps to the P/T marking
    counting each (place, colour) pair.
    """
    net = PTNet(f"{cpn.name}_unfolded")
    for p, pl in cpn.places.items():
        for c in pl.colour_set.values:
            net.add_place(unfolded_place(p, c), pl.initial[c])
    for t, tr in cpn.transitions.items():
        for b in cpn.all_bindings(t):
            if tr.guard is not None and not tr.guard(b):
                continue
            pre: dict[str, int] = {}
            post: dict[str, int] = {}
            for arcs, target in ((tr.inputs, pre), (tr.outputs, post)):
                for p, expr in arcs.items():
                    for c, n in cpn._arc(expr, b, p).items():
                        name = unfolded_place(p, c)
                        target[name] = target.get(name, 0) + n
            net.add_transition(binding_label(t, b), pre, post)
    return net


def to_pt_marking(cpn: CPN, net: PTNet, m: FrozenMarking) -> tuple[int, ...]:
    """Map a CPN marking onto the places of ``unfold(cpn)``."""
    counts = {
        unfolded_place(p, c): n for p, items in m for c, n in items
    }  # fmt: skip
    return tuple(counts.get(p, 0) for p in net.places)
