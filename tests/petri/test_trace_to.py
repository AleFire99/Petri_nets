from petrilab.petri import examples


def test_shortest_trace_to_deadlock() -> None:
    net = examples.dining_philosophers(2)
    trace = net.trace_to(lambda m: not net.enabled_transitions(m))
    assert trace == ["takeLeft0", "takeLeft1"]


def test_trace_to_initial_marking_is_empty() -> None:
    net = examples.water()
    assert net.trace_to(lambda m: m == net.initial_marking) == []


def test_unreachable_target_gives_none() -> None:
    net = examples.mutex()
    both = net.marking(Crit1=1, Crit2=1)
    assert net.trace_to(lambda m: m == both) is None


def test_trace_replays() -> None:
    net = examples.water()
    target = net.marking(H2O=4)
    trace = net.trace_to(lambda m: m == target)
    assert trace == ["react", "react"]
    m = net.initial_marking
    for t in trace:
        m = net.fire(m, t)
    assert m == target
