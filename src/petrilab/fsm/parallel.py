"""Parallel regions: independent text styles. See docs/fsm/parallel.md."""

from statemachine import State, StateChart


class TextStyle(StateChart):
    allow_event_without_transition = False
    catch_errors_as_events = False

    class editing(State.Parallel):
        class bold(State.Compound):
            bold_off = State(initial=True)
            bold_on = State()
            toggle_bold = bold_off.to(bold_on) | bold_on.to(bold_off)

        class italic(State.Compound):
            italic_off = State(initial=True)
            italic_on = State()
            toggle_italic = italic_off.to(italic_on) | italic_on.to(italic_off)

        class underline(State.Compound):
            underline_off = State(initial=True)
            underline_on = State()
            toggle_underline = underline_off.to(underline_on) | underline_on.to(
                underline_off
            )
