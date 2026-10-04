"""Hierarchical media player. See docs/fsm/hierarchical.md."""

from statemachine import State, StateChart


class MediaPlayer(StateChart):
    allow_event_without_transition = False
    catch_errors_as_events = False

    off = State(initial=True)

    class on(State.Compound):
        stopped = State(initial=True)
        playing = State()
        paused = State()

        play = stopped.to(playing) | paused.to(playing)
        pause = playing.to(paused)
        stop = playing.to(stopped) | paused.to(stopped)

    power_on = off.to(on)
    power_off = on.to(off)
