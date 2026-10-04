"""Spike: sismic — statechart YAML, history, parallel, simulated clock, guards, property statecharts."""

from sismic.clock import SimulatedClock
from sismic.interpreter import Interpreter
from sismic.io import import_from_yaml

DOOR = """
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
          - guard: after(30) > 0
            target: alarm
      - name: alarm
        transitions:
          - event: close
            target: closed
"""

WASHER = """
statechart:
  name: Washer
  root state:
    name: root
    initial: off
    states:
      - name: off
        transitions:
          - event: start
            target: running
      - name: running
        initial: fill
        transitions:
          - event: pause
            target: paused
          - event: stop
            target: off
        states:
          - name: fill
            transitions:
              - event: filled
                target: wash
          - name: wash
            initial: soak
            transitions:
              - event: washed
                target: spin
            states:
              - name: soak
                transitions:
                  - event: soaked
                    target: agitate
              - name: agitate
          - name: spin
          - name: hist
            type: deep history
            memory: fill
      - name: paused
        transitions:
          - event: resume
            target: hist
"""


def main() -> None:
    clock = SimulatedClock()
    door = Interpreter(import_from_yaml(DOOR), clock=clock)
    door.execute_once()
    door.queue("open").execute()
    clock.time = 29
    door.execute()
    print("t=29:", door.configuration)
    clock.time = 30
    door.execute()
    print("t=30:", door.configuration)

    w = Interpreter(import_from_yaml(WASHER))
    w.execute_once()
    for e in ("start", "filled", "soaked", "pause", "resume"):
        w.queue(e).execute()
    print("washer:", w.configuration)


if __name__ == "__main__":
    main()
