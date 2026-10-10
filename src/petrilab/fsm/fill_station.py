"""Fill station EFSM, hand-written from the verified XState model.

Design: docs/fsm/fill-station.md. Model: xstate/src/machines/fillStation.machine.ts.
Proven equal to the model by replaying xstate/generated/fill-station/vectors.json
(tests/fsm/test_xstate_vectors.py). Plain Python on purpose: the same structure
ports to a PLC function block or a C++ class.
"""

FILL_TIMEOUT_MS = 30_000
HEAT_TIMEOUT_MS = 60_000
SETTLE_TIME_MS = 5_000
MAX_RETRIES = 2

# state -> (delay in ms, fault code or None, target)
_TIMERS: dict[str, tuple[int, str | None, str]] = {
    "running.filling": (FILL_TIMEOUT_MS, "FILL_TIMEOUT", "fault"),
    "running.heating": (HEAT_TIMEOUT_MS, "HEAT_TIMEOUT", "fault"),
    "running.settling": (SETTLE_TIME_MS, None, "running.draining"),
}

# Moore outputs: state -> energised outputs
_OUTPUTS: dict[str, frozenset[str]] = {
    "running.filling": frozenset({"INLET"}),
    "running.heating": frozenset({"HEATER"}),
    "running.draining": frozenset({"OUTLET"}),
}


class FillStation:
    def __init__(self) -> None:
        self.state = "idle"
        self.retries = 0
        self.last_fault: str | None = None
        self._elapsed_ms = 0  # time spent in the current state

    @property
    def outputs(self) -> frozenset[str]:
        return _OUTPUTS.get(self.state, frozenset())

    def send(self, event: str) -> None:
        """Process one event. Unhandled events are ignored, as in XState."""
        s = self.state
        if event == "ESTOP":  # root-level transition, from any state
            self._go("emergency")
        elif s == "idle" and event == "START":
            self._go("running.filling")
        elif s == "running.filling" and event == "LEVEL_HIGH":
            self._go("running.heating")
        elif s == "running.heating" and event == "TEMP_OK":
            self._go("running.settling")
        elif (s == "running.draining" and event == "LEVEL_LOW") or (
            s.startswith("running.") and event == "STOP"  # inherited from `running`
        ):
            self._go("idle")
        elif s == "fault" and event == "RESET":
            if self.retries < MAX_RETRIES:
                self.retries += 1
                self._go("idle")
            else:
                self._go("lockedOut")
        elif s == "lockedOut" and event == "MAINT_RESET":
            self.retries, self.last_fault = 0, None
            self._go("idle")
        elif s == "emergency" and event == "ESTOP_RELEASE":
            self._go("idle")

    def tick(self, ms: int) -> None:
        """Advance time; fires the current state's timer when it expires."""
        self._elapsed_ms += ms
        timer = _TIMERS.get(self.state)
        if timer and self._elapsed_ms >= timer[0]:
            _, fault, target = timer
            if fault:
                self.last_fault = fault
            self._go(target)

    def _go(self, target: str) -> None:
        if target != self.state:
            self._elapsed_ms = 0
        self.state = target
