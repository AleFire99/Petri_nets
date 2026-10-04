"""Washing machine with shallow and deep history. See docs/fsm/history.md."""

from statemachine import HistoryState, State, StateChart


class _WasherBase(StateChart):
    allow_event_without_transition = False
    catch_errors_as_events = False


class WasherDeep(_WasherBase):
    off = State(initial=True)

    class running(State.Compound):
        fill = State(initial=True)

        class wash(State.Compound):
            soak = State(initial=True)
            agitate = State()
            soaked = soak.to(agitate)

        spin = State()
        hist = HistoryState(type="deep")
        filled = fill.to(wash)
        washed = wash.to(spin)

    paused = State()

    start = off.to(running)
    pause = running.to(paused)
    resume = paused.to(running.hist)  # type: ignore[attr-defined]
    stop = running.to(off) | paused.to(off)


class WasherShallow(_WasherBase):
    off = State(initial=True)

    class running(State.Compound):
        fill = State(initial=True)

        class wash(State.Compound):
            soak = State(initial=True)
            agitate = State()
            soaked = soak.to(agitate)

        spin = State()
        hist = HistoryState(type="shallow")
        filled = fill.to(wash)
        washed = wash.to(spin)

    paused = State()

    start = off.to(running)
    pause = running.to(paused)
    resume = paused.to(running.hist)  # type: ignore[attr-defined]
    stop = running.to(off) | paused.to(off)
