"""System behaviour of a timed, hierarchical EFSM: the fill station (docs/fsm/fill-station.md).

Run: uv run python examples/fill_station_behaviour.py
Time is simulated with tick(ms): no real clock, fully reproducible.
"""

from petrilab.fsm.fill_station import FILL_TIMEOUT_MS, FillStation


def show(fs: FillStation, what: str) -> None:
    print(f"  {what:<28} state={fs.state:<17} outputs={sorted(fs.outputs)} "
          f"retries={fs.retries} last_fault={fs.last_fault}")  # fmt: skip


def main() -> None:
    print("-- normal cycle")
    fs = FillStation()
    show(fs, "start")
    for ev in ["START", "LEVEL_HIGH", "TEMP_OK"]:
        fs.send(ev)
        show(fs, ev)
    fs.tick(4_999)
    show(fs, "tick 4999 ms (settling)")
    fs.tick(1)
    show(fs, "tick 1 ms (settle done)")
    fs.send("LEVEL_LOW")
    show(fs, "LEVEL_LOW")

    print("\n-- fill timeout, retries, lock-out")
    fs = FillStation()
    for attempt in range(3):
        fs.send("START")
        fs.tick(FILL_TIMEOUT_MS)
        show(fs, f"attempt {attempt + 1}: timeout")
        fs.send("RESET")
        show(fs, "RESET")
    fs.send("MAINT_RESET")
    show(fs, "MAINT_RESET")

    print("\n-- emergency stop from anywhere")
    fs = FillStation()
    fs.send("START")
    fs.send("ESTOP")
    show(fs, "START, ESTOP")
    fs.send("START")
    show(fs, "START (ignored)")
    fs.send("ESTOP_RELEASE")
    show(fs, "ESTOP_RELEASE")


if __name__ == "__main__":
    main()
