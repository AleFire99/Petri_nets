"""Moore vs Mealy "11" detectors. See docs/fsm/moore-mealy.md."""

from collections.abc import Iterable
from typing import ClassVar

from statemachine import State, StateChart

MEALY: dict[tuple[str, int], tuple[str, int]] = {
    ("S0", 0): ("S0", 0),
    ("S0", 1): ("S1", 0),
    ("S1", 0): ("S0", 0),
    ("S1", 1): ("S1", 1),
}


class MealyDetector:
    """Output depends on (state, input): a plain transition table."""

    def __init__(self) -> None:
        self.state = "S0"

    def step(self, bit: int) -> int:
        self.state, out = MEALY[(self.state, bit)]
        return out

    def run(self, bits: Iterable[int]) -> list[int]:
        return [self.step(b) for b in bits]


class MooreDetector(StateChart):
    """Output depends on the state only."""

    allow_event_without_transition = False
    catch_errors_as_events = False

    a = State(initial=True)
    b = State()
    c = State()

    zero = a.to.itself() | b.to(a) | c.to(a)
    one = a.to(b) | b.to(c) | c.to.itself()

    OUTPUT: ClassVar[dict[str, int]] = {"a": 0, "b": 0, "c": 1}

    @property
    def output(self) -> int:
        return self.OUTPUT[next(iter(self.configuration)).id]

    def run(self, bits: Iterable[int]) -> list[int]:
        out = []
        for bit in bits:
            self.send("one" if bit else "zero")
            out.append(self.output)
        return out
