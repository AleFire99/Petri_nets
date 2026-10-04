from petrilab.petri import analysis, examples
from petrilab.petri.snakes_bridge import explore, to_snakes


def test_inhibitor_bounds_the_counter() -> None:
    n = examples.bounded_counter()
    space = explore(to_snakes(n), token_cap=10)
    assert analysis.is_bounded(space)
    assert analysis.max_tokens(space, "Buf") == 2
    assert len(space) == 3
    assert analysis.is_deadlock_free(space)
    assert analysis.is_live(space, set(n.transitions))


def test_without_inhibitor_unbounded() -> None:
    space = explore(to_snakes(examples.bounded_counter(inhibited=False)), token_cap=10)
    assert not analysis.is_bounded(space)


def test_read_arc_does_not_consume_key() -> None:
    n = examples.read_arc_net()
    g = n.reachable()
    assert set(g) == {
        n.marking(Key=1, Job=2),
        n.marking(Key=1, Job=1, Done=1),
        n.marking(Key=1, Done=2),
    }
    assert all(m[0] == 1 for m in g)
    assert [m for m, s in g.items() if not s] == [n.marking(Key=1, Done=2)]


def test_read_arc_without_key_is_dead_from_start() -> None:
    n = examples.read_arc_net(key=False)
    assert n.reachable() == {n.initial_marking: []}
