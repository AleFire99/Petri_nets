"""Bridge to SNAKES: compile a PTNet, and explore the reachability graph of any SNAKES net."""

from collections import deque
from dataclasses import dataclass, field

import networkx as nx
from snakes.nets import Inhibitor, MultiArc, PetriNet, Place, Test, Transition, Value
from snakes.nets import Marking as SnakesMarking

from petrilab.petri.model import PTNet, StateSpaceLimitError

MarkingKey = tuple[tuple[str, tuple[str, ...]], ...]


def marking_key(m: SnakesMarking) -> MarkingKey:
    """Canonical, hashable form of a SNAKES marking (tokens compared by repr)."""
    return tuple(
        (place, tuple(sorted(repr(tok) for tok in tokens)))
        for place, tokens in sorted(m.items())
    )


@dataclass
class StateSpace:
    """Reachability graph: nodes are marking keys, edges are labelled by transition name."""

    graph: "nx.MultiDiGraph[MarkingKey]"
    initial: MarkingKey
    markings: dict[MarkingKey, SnakesMarking] = field(default_factory=dict)
    exceeded_cap: bool = (
        False  # True if some place exceeded the token cap (unbounded suspect)
    )

    def tokens(self, key: MarkingKey, place: str) -> int:
        marking = self.markings[key]
        return (
            len(marking[place]) if place in marking else 0
        )  # SNAKES omits empty places

    def __len__(self) -> int:
        return self.graph.number_of_nodes()


def _arc(w: int) -> Value | MultiArc:
    return Value(1) if w == 1 else MultiArc([Value(1)] * w)


def to_snakes(net: PTNet) -> PetriNet:
    sn = PetriNet(net.name)
    for p, tokens in net.places.items():
        sn.add_place(Place(p, [1] * tokens))
    for t, spec in net.transitions.items():
        sn.add_transition(Transition(t))
        for p, w in spec.pre.items():
            sn.add_input(p, t, _arc(w))
        for p, w in spec.post.items():
            sn.add_output(p, t, _arc(w))
        for p, w in spec.inhibit.items():
            sn.add_input(p, t, Inhibitor(_arc(w)))
        for p, w in spec.read.items():
            sn.add_input(p, t, Test(_arc(w)))
        if not (spec.pre or spec.read or spec.inhibit):
            # SNAKES finds no firing modes for a transition without input arcs: give source
            # transitions a hidden always-marked place read through a test arc.
            hidden = f"__source_{t}"
            sn.add_place(Place(hidden, [1]))
            sn.add_input(hidden, t, Test(Value(1)))
    return sn


def explore(
    net: PetriNet, *, max_states: int = 100_000, token_cap: int | None = None
) -> StateSpace:
    """Breadth-first reachability. Stops early if a place exceeds ``token_cap`` tokens."""
    start = net.get_marking()
    k0 = marking_key(start)
    space = StateSpace(nx.MultiDiGraph(), k0, {k0: start})
    space.graph.add_node(k0)
    queue = deque([k0])
    while queue:
        key = queue.popleft()
        marking = space.markings[key]
        for tname in net.transition():
            trans = net.transition(tname.name)
            net.set_marking(marking)
            for mode in list(
                trans.modes()
            ):  # materialise: firing below mutates the net
                net.set_marking(marking)
                trans.fire(mode)
                nxt = net.get_marking()
                nk = marking_key(nxt)
                if nk not in space.markings:
                    if len(space.markings) >= max_states:
                        raise StateSpaceLimitError(f"more than {max_states} states")
                    space.markings[nk] = nxt
                    space.graph.add_node(nk)
                    if token_cap is not None and any(
                        len(v) > token_cap for v in nxt.values()
                    ):
                        space.exceeded_cap = True
                        net.set_marking(start)
                        space.graph.add_edge(key, nk, transition=trans.name)
                        return space
                    queue.append(nk)
                space.graph.add_edge(key, nk, transition=trans.name)
    net.set_marking(start)
    return space
