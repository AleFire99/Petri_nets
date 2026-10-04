"""Coloured net example (docs/petri/colored.md), built directly with SNAKES."""

from snakes.nets import Expression, PetriNet, Place, Transition, Variable


def jobs_net(jobs: tuple[int, ...] = (1, 2, 3)) -> PetriNet:
    """``square`` consumes a job ``n`` with guard ``n > 1`` and produces ``n*n``."""
    net = PetriNet("jobs")
    net.add_place(Place("Jobs", list(jobs)))
    net.add_place(Place("Results", []))
    net.add_transition(Transition("square", Expression("n > 1")))
    net.add_input("Jobs", "square", Variable("n"))
    net.add_output("Results", "square", Expression("n*n"))
    return net
