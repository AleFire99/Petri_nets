from petrilab.petri import analysis
from petrilab.petri.colored import jobs_net
from petrilab.petri.snakes_bridge import explore


def test_guard_blocks_job_one() -> None:
    space = explore(jobs_net())
    assert len(space) == 4
    dead = analysis.dead_markings(space)
    assert len(dead) == 1
    final = space.markings[dead[0]]
    assert sorted(final["Jobs"]) == [1]
    assert sorted(final["Results"]) == [4, 9]


def test_only_guarded_jobs_fire() -> None:
    space = explore(jobs_net((1,)))
    assert len(space) == 1
    assert analysis.fired_transitions(space) == set()


def test_all_jobs_processed_when_guard_satisfied() -> None:
    space = explore(jobs_net((2, 3, 4)))
    (dead,) = analysis.dead_markings(space)
    assert sorted(space.markings[dead]["Results"]) == [4, 9, 16]
    assert space.tokens(dead, "Jobs") == 0
