"""Spike: python-statemachine 3.x — hierarchy, deep/shallow history, parallel, guards, diagram."""

from statemachine import HistoryState, State, StateChart


class Washer(StateChart):
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
    resume = paused.to(running.hist)  # type: ignore[attr-defined]

    start = off.to(running)
    pause = running.to(paused)
    stop = running.to(off) | paused.to(off)


class Styles(StateChart):
    class editing(State.Parallel):
        class bold(State.Compound):
            bold_off = State(initial=True)
            bold_on = State()
            toggle_bold = bold_off.to(bold_on) | bold_on.to(bold_off)

        class italic(State.Compound):
            italic_off = State(initial=True)
            italic_on = State()
            toggle_italic = italic_off.to(italic_on) | italic_on.to(italic_off)


def main() -> None:
    w = Washer()
    print("initial:", sorted(s.id for s in w.configuration))
    w.send("start")
    w.send("filled")
    w.send("soaked")
    print("running:", sorted(s.id for s in w.configuration))
    w.send("pause")
    print("paused:", sorted(s.id for s in w.configuration))
    w.send("resume")
    print("resumed:", sorted(s.id for s in w.configuration))
    s = Styles()
    s.send("toggle_bold")
    print("parallel:", sorted(x.id for x in s.configuration))
    from statemachine.contrib.diagram import MermaidGraphMachine

    print(MermaidGraphMachine(Washer()).get_mermaid()[:300])


if __name__ == "__main__":
    main()
