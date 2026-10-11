"""Solution E4 (advanced): model-based test generation, mutation testing, EFSM -> CPN.
Statement: exercises/efsm/e4-test-generation.md

Answers:
1. transition_cover() explores the PIN lock and emits one vector per edge of the
   configuration graph: the shortest path to the edge's source, then the edge. 8 edges ->
   8 vectors; every step records the expected (state, context).
2. The hand-written PinLockImpl (plain if/else, no engine) passes all 8 vectors.
3. Mutants: blocking after 4 wrong PINs, and forgetting to reset `attempts` on success,
   are both killed: at least one vector fails for each.
4. EFSM as a CPN: one place Ctrl with colour set S x {0..3}, one token (state, attempts);
   one CPN transition per event instance with guard and output arc from the EFSM.
   The CPN has 5 reachable markings, the same as the EFSM's 5 configurations.
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from petrilab.fsm.efsm import EFSM, Configuration, Event, explore
from petrilab.petri.cpn import CPN, Binding, ColourSet

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e2_pin_lock import EVENTS, SECRET, pin_lock


@dataclass
class Vector:
    events: list[Event]
    expected: list[tuple[str, dict[str, Any]]]


def transition_cover(
    efsm: EFSM, events: list[Event], max_depth: int | None = None
) -> list[Vector]:
    r = explore(efsm, events, max_depth=max_depth)
    vectors = []
    for src, ev, _ in r.edges:
        path = [*r.path_to(src), ev]
        config, expected = efsm.initial_configuration, []
        for e in path:
            nxt = efsm.step(config, e)
            assert nxt is not None  # every path in the configuration graph is feasible
            config = nxt
            expected.append((config.state, config.ctx))
        vectors.append(Vector(path, expected))
    return vectors


class PinLockImpl:
    """Hand-written implementation under test (could be C, ST, ...)."""

    def __init__(self, block_after: int = 3, reset_on_success: bool = True) -> None:
        self.state, self.attempts = "locked", 0
        self.block_after, self.reset_on_success = block_after, reset_on_success

    def send(self, ev: Event) -> None:
        if self.state == "locked" and ev["type"] == "enter":
            if ev["pin"] == SECRET:
                self.state = "unlocked"
                if self.reset_on_success:
                    self.attempts = 0
            else:
                self.attempts += 1
                if self.attempts >= self.block_after:
                    self.state = "blocked"
        elif self.state == "unlocked" and ev["type"] == "lock":
            self.state = "locked"
        elif self.state == "blocked" and ev["type"] == "admin_reset":
            self.state, self.attempts = "locked", 0


def passes(impl_factory: Any, vectors: list[Vector]) -> bool:
    for v in vectors:
        impl = impl_factory()
        for ev, (state, ctx) in zip(v.events, v.expected, strict=True):
            impl.send(ev)
            if (impl.state, {"attempts": impl.attempts}) != (state, ctx):
                return False
    return True


def efsm_as_cpn(efsm: EFSM, events: list[Event], domain: tuple[Any, ...]) -> CPN:
    """Single-token CPN: Ctrl holds (state, attempts); one transition per event instance."""
    ctrl = ColourSet("CTRL", tuple((s, a) for s in efsm.states for a in domain))
    net = CPN(f"{efsm.name}_cpn")
    init = efsm.initial_configuration
    net.add_place("Ctrl", ctrl, [(init.state, init.ctx["attempts"])])
    for i, ev in enumerate(events):

        def fires(b: Binding, ev: Event = ev) -> bool:
            s, a = b["c"]
            return efsm.step(Configuration.of(s, {"attempts": a}), ev) is not None

        def target(b: Binding, ev: Event = ev) -> list[tuple[str, int]]:
            s, a = b["c"]
            nxt = efsm.step(Configuration.of(s, {"attempts": a}), ev)
            assert nxt is not None
            return [(nxt.state, nxt.ctx["attempts"])]

        net.add_transition(f"e{i}_{ev['type']}", variables={"c": ctrl}, guard=fires,
                           inputs={"Ctrl": lambda b: [b["c"]]}, outputs={"Ctrl": target})  # fmt: skip
    return net


def check() -> None:
    vectors = transition_cover(pin_lock(), EVENTS)
    assert len(vectors) == 8
    assert passes(PinLockImpl, vectors)
    assert not passes(lambda: PinLockImpl(block_after=4), vectors)
    assert not passes(lambda: PinLockImpl(reset_on_success=False), vectors)

    cpn = efsm_as_cpn(pin_lock(), EVENTS, (0, 1, 2, 3))
    graph = cpn.reachable()
    assert len(graph) == explore(pin_lock(), EVENTS).state_count == 5
    assert all(
        sum(n for _, n in m[0][1]) == 1 for m in graph
    )  # always exactly one token


if __name__ == "__main__":
    check()
    for v in transition_cover(pin_lock(), EVENTS):
        print(
            [e["type"] + (f"({e['pin']})" if "pin" in e else "") for e in v.events],
            "->",
            v.expected[-1],
        )
    print("E4 OK")
