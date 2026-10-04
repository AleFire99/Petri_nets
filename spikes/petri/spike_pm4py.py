"""Spike: PM4Py — build WF-nets, check soundness (woflan), reachability graph."""

from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.petri_net.utils import petri_utils as pu


def build(name: str, places: list[str], trans: list[str], arcs: list[tuple[str, str]]):
    net = PetriNet(name)
    nodes: dict[str, PetriNet.Place | PetriNet.Transition] = {}
    for p in places:
        nodes[p] = PetriNet.Place(p)
        net.places.add(nodes[p])
    for t in trans:
        nodes[t] = PetriNet.Transition(t, t)
        net.transitions.add(nodes[t])
    for a, b in arcs:
        pu.add_arc_from_to(nodes[a], nodes[b], net)
    return net, Marking({nodes["i"]: 1}), Marking({nodes["o"]: 1})


def main() -> None:
    import pm4py

    sound = build(
        "sound",
        ["i", "a", "b", "a2", "b2", "o"],
        ["register", "checkA", "checkB", "decide"],
        [
            ("i", "register"),
            ("register", "a"),
            ("register", "b"),
            ("a", "checkA"),
            ("b", "checkB"),
            ("checkA", "a2"),
            ("checkB", "b2"),
            ("a2", "decide"),
            ("b2", "decide"),
            ("decide", "o"),
        ],
    )
    unsound = build(
        "unsound",
        ["i", "pa", "pb", "o"],
        ["chooseA", "chooseB", "join"],
        [
            ("i", "chooseA"),
            ("i", "chooseB"),
            ("chooseA", "pa"),
            ("chooseB", "pb"),
            ("pa", "join"),
            ("pb", "join"),
            ("join", "o"),
        ],
    )
    for label, (net, im, fm) in (("sound", sound), ("unsound", unsound)):
        print(label, pm4py.check_soundness(net, im, fm))


if __name__ == "__main__":
    main()
