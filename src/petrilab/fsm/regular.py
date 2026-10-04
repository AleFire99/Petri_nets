"""Regular (flat) FSMs: traffic light and turnstile. See docs/fsm/regular.md."""

from statemachine import State, StateChart


class TrafficLight(StateChart):
    allow_event_without_transition = False
    catch_errors_as_events = False

    red = State(initial=True)
    green = State()
    yellow = State()

    next = red.to(green) | green.to(yellow) | yellow.to(red)


class Turnstile(StateChart):
    allow_event_without_transition = False
    catch_errors_as_events = False

    locked = State(initial=True)
    unlocked = State()

    coin = locked.to(unlocked) | unlocked.to.itself()
    push = unlocked.to(locked) | locked.to.itself()
