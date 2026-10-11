"""A small, generic extended finite state machine (EFSM) engine (docs/fsm/efsm-formal.md).

An EFSM is a tuple ``(S, s0, V, c0, E, T)``:

- ``S`` finite control states, ``s0`` the initial one;
- ``V`` context variables with initial valuation ``c0``;
- ``E`` events, each carrying an optional payload (``{"type": "insert", "amount": 25}``);
- ``T`` transitions ``(source, event, guard, action, target)``: the guard is a predicate on
  (context, event), the action returns the context updates.

A *configuration* is ``(state, context)``; it is the real "state" of the machine.

Semantics follow XState v5, so the Python machines replay the XState test vectors 1:1:
transitions are tried in declaration order and the first enabled one fires; an event with
no enabled transition is ignored (``strict=True`` raises instead). Guards and actions must be
pure functions: the engine never mutates a context in place.

``explore`` enumerates configurations breadth-first, like ``xstate/src/analysis/explore.ts``
(same counting rules), for deadlock, invariant and reachability checks.
"""

from collections import deque
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

Context = Mapping[str, Any]
Event = Mapping[str, Any]
"""``{"type": name, **payload}``, the XState event shape."""
Guard = Callable[[Context, Event], bool]
Action = Callable[[Context, Event], Mapping[str, Any]]
"""Returns only the variables it changes (like XState ``assign``)."""


class UnknownEventError(ValueError):
    """Event type not in the machine's alphabet: a caller bug, always raised."""


class InvalidTransitionError(RuntimeError):
    """Known event with no enabled transition in the current configuration (strict mode)."""


@dataclass(frozen=True)
class Transition:
    source: str
    event: str
    target: str
    guard: Guard | None = None
    action: Action | None = None
    label: str = ""  # human-readable guard/action, e.g. "[credit >= price] / dispense"

    def __str__(self) -> str:
        return f"{self.source} --{self.event}{' ' + self.label if self.label else ''}--> {self.target}"


@dataclass(frozen=True)
class Configuration:
    """Hashable (state, context) pair. Context values must be hashable."""

    state: str
    context: tuple[tuple[str, Any], ...]

    @classmethod
    def of(cls, state: str, context: Context) -> "Configuration":
        return cls(state, tuple(sorted(context.items())))

    @property
    def ctx(self) -> dict[str, Any]:
        return dict(self.context)

    def __str__(self) -> str:
        values = ", ".join(f"{k}={v!r}" for k, v in self.context)
        return f"{self.state} {{{values}}}"


def event_label(e: Event) -> str:
    """``insert(amount=25)``, same format as the XState explorer."""
    payload = [f"{k}={v!r}" for k, v in e.items() if k != "type"]
    return f"{e['type']}({', '.join(payload)})" if payload else str(e["type"])


class EFSM:
    def __init__(
        self,
        name: str,
        states: Iterable[str],
        initial: str,
        context: Context,
        transitions: Iterable[Transition],
    ) -> None:
        self.name = name
        self.states = tuple(states)
        self.initial = initial
        self.initial_context = dict(context)
        self.transitions = tuple(transitions)
        self._validate()

    def _validate(self) -> None:
        if len(set(self.states)) != len(self.states):
            raise ValueError("duplicate state names")
        if self.initial not in self.states:
            raise ValueError(f"initial state {self.initial!r} not in states")
        for t in self.transitions:
            for s in (t.source, t.target):
                if s not in self.states:
                    raise ValueError(f"transition {t} uses unknown state {s!r}")
        for k, v in self.initial_context.items():
            try:
                hash(v)
            except TypeError as exc:
                raise ValueError(f"context variable {k!r} must be hashable") from exc

    @property
    def events(self) -> tuple[str, ...]:
        """Input alphabet: every event type that appears on some transition, sorted."""
        return tuple(sorted({t.event for t in self.transitions}))

    @property
    def initial_configuration(self) -> Configuration:
        return Configuration.of(self.initial, self.initial_context)

    def candidates(self, config: Configuration, event: Event) -> list[Transition]:
        """Every transition enabled for ``event`` in ``config``, in priority order."""
        if event["type"] not in self.events:
            raise UnknownEventError(f"{event['type']!r} not in alphabet {self.events}")
        ctx = config.ctx
        return [
            t
            for t in self.transitions
            if t.source == config.state
            and t.event == event["type"]
            and (t.guard is None or t.guard(ctx, event))
        ]

    def select(self, config: Configuration, event: Event) -> Transition | None:
        """The transition that fires: the first enabled one (declaration order)."""
        enabled = self.candidates(config, event)
        return enabled[0] if enabled else None

    def step(self, config: Configuration, event: Event) -> Configuration | None:
        """Pure successor function; ``None`` if the event is ignored."""
        t = self.select(config, event)
        if t is None:
            return None
        ctx = config.ctx
        if t.action is not None:
            updates = t.action(ctx, event)
            unknown = set(updates) - set(ctx)
            if unknown:
                raise KeyError(
                    f"action of {t} writes undeclared variables {sorted(unknown)}"
                )
            ctx = {**ctx, **updates}
        return Configuration.of(t.target, ctx)


class Machine:
    """A running instance of an EFSM: current configuration plus a trace."""

    def __init__(self, efsm: EFSM, *, strict: bool = False) -> None:
        self.efsm = efsm
        self.strict = strict
        self.config = efsm.initial_configuration
        self.trace: list[str] = []

    @property
    def state(self) -> str:
        return self.config.state

    @property
    def context(self) -> dict[str, Any]:
        return self.config.ctx

    def send(self, event: Event | str, **payload: Any) -> bool:
        """Process one event. Returns True if a transition fired.

        ``send("insert", amount=25)`` and ``send({"type": "insert", "amount": 25})`` are the
        same. An ignored event leaves the configuration unchanged (or raises in strict mode).
        """
        ev: Event = {"type": event, **payload} if isinstance(event, str) else event
        nxt = self.efsm.step(self.config, ev)
        if nxt is None:
            if self.strict:
                raise InvalidTransitionError(
                    f"no transition for {event_label(ev)} in {self.config}"
                )
            return False
        self.config = nxt
        self.trace.append(event_label(ev))
        return True

    def reset(self) -> None:
        self.config = self.efsm.initial_configuration
        self.trace.clear()


@dataclass
class Exploration:
    """Explored part of the configuration graph."""

    initial: Configuration
    depth: dict[Configuration, int] = field(default_factory=dict)
    edges: list[tuple[Configuration, Event, Configuration]] = field(
        default_factory=list
    )
    parent: dict[Configuration, tuple[Configuration, Event] | None] = field(
        default_factory=dict
    )
    frontier: set[Configuration] = field(default_factory=set)
    truncated: bool = False

    @property
    def configurations(self) -> list[Configuration]:
        return list(self.depth)

    @property
    def state_count(self) -> int:
        return len(self.depth)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def depth_limited(self) -> bool:
        """True if a depth bound cut the search (results hold for the explored part only)."""
        return bool(self.frontier)

    def path_to(self, config: Configuration) -> list[Event]:
        steps: list[Event] = []
        cur = self.parent[config]
        while cur is not None:
            prev, ev = cur
            steps.append(ev)
            cur = self.parent[prev]
        return steps[::-1]

    def deadlocks(self) -> list[Configuration]:
        """Fully expanded configurations where every event is ignored."""
        has_out = {src for src, _, _ in self.edges}
        return [c for c in self.depth if c not in self.frontier and c not in has_out]

    def violations(
        self, invariants: Mapping[str, Callable[[Configuration], bool]]
    ) -> list[tuple[str, Configuration, list[str]]]:
        """(invariant name, violating configuration, shortest event trace)."""
        return [
            (name, c, [event_label(e) for e in self.path_to(c)])
            for c in self.depth
            for name, pred in invariants.items()
            if not pred(c)
        ]

    def visited_states(self) -> set[str]:
        return {c.state for c in self.depth}


def explore(
    efsm: EFSM,
    events: Sequence[Event],
    *,
    max_depth: int | None = None,
    max_states: int = 50_000,
) -> Exploration:
    """Breadth-first exploration trying every event in ``events`` in every configuration.

    Each payload variant is a separate event. Self-loops that leave the configuration
    unchanged are not edges (same rule as the XState explorer), so counts are comparable
    with ``xstate/generated/reports``.
    """
    start = efsm.initial_configuration
    r = Exploration(start, {start: 0}, parent={start: None})
    queue = deque([start])
    while queue:
        c = queue.popleft()
        if max_depth is not None and r.depth[c] >= max_depth:
            r.frontier.add(c)
            continue
        for ev in events:
            nxt = efsm.step(c, ev)
            if nxt is None or nxt == c:
                continue
            r.edges.append((c, ev, nxt))
            if nxt not in r.depth:
                if len(r.depth) >= max_states:
                    r.truncated = True
                    continue
                r.depth[nxt] = r.depth[c] + 1
                r.parent[nxt] = (c, ev)
                queue.append(nxt)
    return r


def nondeterministic_choices(
    efsm: EFSM, exploration: Exploration, events: Sequence[Event]
) -> list[tuple[Configuration, str, list[str]]]:
    """Places where more than one transition is enabled (resolved by priority).

    A textbook EFSM requires mutually exclusive guards; XState (and this engine) accept
    overlaps and take the first. This lists every overlap so you can decide if it is meant.
    """
    found = []
    for c in exploration.configurations:
        for ev in events:
            enabled = efsm.candidates(c, ev)
            if len(enabled) > 1:
                found.append((c, event_label(ev), [str(t) for t in enabled]))
    return found
