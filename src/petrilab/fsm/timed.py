"""Timed FSM: door alarm using sismic with an injectable clock. See docs/fsm/timed.md."""

from sismic.clock import SimulatedClock
from sismic.interpreter import Interpreter
from sismic.io import import_from_yaml

TIMEOUT_S = 30

_DOOR_YAML = f"""
statechart:
  name: Door
  root state:
    name: root
    initial: closed
    states:
      - name: closed
        transitions:
          - event: open
            target: open
      - name: open
        transitions:
          - event: close
            target: closed
          - guard: after({TIMEOUT_S}) > 0
            target: alarm
      - name: alarm
        transitions:
          - event: close
            target: closed
"""


class DoorAlarm:
    def __init__(self, clock: SimulatedClock | None = None) -> None:
        self.clock = clock or SimulatedClock()
        self._interpreter = Interpreter(import_from_yaml(_DOOR_YAML), clock=self.clock)
        self._interpreter.execute_once()

    @property
    def state(self) -> str:
        (leaf,) = (s for s in self._interpreter.configuration if s != "root")
        return str(leaf)

    def send(self, event: str) -> None:
        if event not in ("open", "close"):
            raise ValueError(f"unknown event {event!r}")
        self._interpreter.queue(event).execute()

    def advance(self, seconds: float) -> None:
        self.clock.time += seconds
        self._interpreter.execute()
