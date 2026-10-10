"""Spike: SNAKES — weighted arcs, inhibitor/read arcs, colours + guards, state graph, dead markings."""

from snakes.nets import (
    Expression,
    Inhibitor,
    MultiArc,
    PetriNet,
    Place,
    StateGraph,
    Test,
    Transition,
    Value,
    Variable,
)


def dead_states(g: StateGraph) -> list[int]:
    return [i for i in g if not any(True for _ in g.successors(i))]


def explore(net: PetriNet) -> StateGraph:
    g = StateGraph(net)
    g.build()
    return g


def main() -> None:
    water = PetriNet("water")
    water.add_place(Place("H2", [1] * 4))
    water.add_place(Place("O2", [1] * 2))
    water.add_place(Place("H2O", []))
    water.add_transition(Transition("react"))
    water.add_input("H2", "react", MultiArc([Value(1), Value(1)]))
    water.add_input("O2", "react", Value(1))
    water.add_output("H2O", "react", MultiArc([Value(1), Value(1)]))
    g = explore(water)
    print("water: states", len(g), "dead", dead_states(g))

    cpn = PetriNet("cpn")
    cpn.add_place(Place("Jobs", [1, 2, 3]))
    cpn.add_place(Place("Results", []))
    cpn.add_transition(Transition("square", Expression("n > 1")))
    cpn.add_input("Jobs", "square", Variable("n"))
    cpn.add_output("Results", "square", Expression("n*n"))
    g = explore(cpn)
    print("cpn: states", len(g), "dead", dead_states(g))

    inhib = PetriNet("inhib")
    inhib.add_place(Place("Buf", []))
    inhib.add_transition(Transition("put"))
    inhib.add_transition(Transition("get"))
    inhib.add_output("Buf", "put", Value(1))
    inhib.add_input("Buf", "get", Value(1))
    inhib.add_input("Buf", "put", Inhibitor(MultiArc([Value(1), Value(1)])))
    g = explore(inhib)
    print("inhibitor: states", len(g), "dead", dead_states(g))

    read = PetriNet("read")
    read.add_place(Place("Key", [1]))
    read.add_place(Place("Job", [1, 1]))
    read.add_place(Place("Done", []))
    read.add_transition(Transition("use"))
    read.add_input("Key", "use", Test(Value(1)))
    read.add_input("Job", "use", Value(1))
    read.add_output("Done", "use", Value(1))
    g = explore(read)
    print("read: states", len(g), "dead", dead_states(g))


if __name__ == "__main__":
    main()
