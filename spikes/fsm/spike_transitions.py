"""Spike: transitions — hierarchy, parallel, guards, timeout, history (manual), markup export."""

import time

from transitions.extensions import HierarchicalMachine
from transitions.extensions.states import Timeout, add_state_features

WASHER = {
    "name": "running",
    "initial": "fill",
    "children": [
        "fill",
        {"name": "wash", "initial": "soak", "children": ["soak", "agitate"]},
        "spin",
    ],
}


@add_state_features(Timeout)
class TimedMachine(HierarchicalMachine):
    pass


def main() -> None:
    m = HierarchicalMachine(
        states=["off", WASHER, "paused"], initial="off", auto_transitions=False
    )
    m.add_transition("start", "off", "running")
    m.add_transition("filled", "running_fill", "running_wash")
    m.add_transition("soaked", "running_wash_soak", "running_wash_agitate")
    m.add_transition(
        "pause", "running", "paused"
    )  # parent transition applies to all children
    m.start()
    m.filled()
    m.soaked()
    print("state:", m.state)
    try:
        m.pause()
        print("paused:", m.state)
    except Exception as e:  # noqa: BLE001
        print("pause err:", e)

    # Parallel regions: list of states as a state's initial/children
    p = HierarchicalMachine(
        states=[
            {
                "name": "editing",
                "parallel": [
                    {"name": "bold", "states": ["off", "on"], "initial": "off"},
                    {"name": "italic", "states": ["off", "on"], "initial": "off"},
                ],
            }
        ],
        initial="editing",
        auto_transitions=False,
    )
    print("parallel:", p.state)

    t = TimedMachine(states=["closed", "open", {"name": "alarm"}], initial="closed")
    t.states["open"].timeout = 0.05  # type: ignore[attr-defined]
    t.states["open"].on_timeout = "to_alarm"  # type: ignore[attr-defined]
    t.to_open()
    time.sleep(0.15)
    print("timeout:", t.state)


if __name__ == "__main__":
    main()
