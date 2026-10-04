from petrilab.petri.workflow import (
    is_sound,
    is_sound_pm4py,
    is_workflow_net,
    parallel_review,
    xor_and_mismatch,
)


def test_both_are_workflow_nets() -> None:
    assert is_workflow_net(parallel_review())
    assert is_workflow_net(xor_and_mismatch())


def test_parallel_review_is_sound() -> None:
    assert is_sound(parallel_review())
    assert is_sound_pm4py(parallel_review())


def test_xor_and_mismatch_is_unsound() -> None:
    n = xor_and_mismatch()
    assert not is_sound(n)
    assert not is_sound_pm4py(xor_and_mismatch())
    g = n.reachable()
    dead = {m for m, s in g.items() if not s}
    assert dead == {n.marking(pa=1), n.marking(pb=1)}


def test_non_workflow_net_detected() -> None:
    n = parallel_review()
    n.add_place("orphan")
    assert not is_workflow_net(n)
    assert not is_sound(n)
