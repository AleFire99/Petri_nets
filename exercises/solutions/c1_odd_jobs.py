"""Solution C1 (beginner): guards and bindings. Statement: exercises/cpn/c1-odd-jobs.md

Answers:
1. Colour set JOB = {0..9}, RESULT = {0, 1, 4, ..., 81}; variable n : JOB;
   guard n mod 2 = 1; input arc n, output arc n*n.
2. In M0 = Jobs{1,2,3,4,5}: enabled bindings n = 1, 3, 5 (2 and 4 fail the guard,
   0, 6..9 have no token).
3. Each odd job is processed independently, in any order: 2^3 = 8 markings, 12 edges
   (each of the 3 jobs fires once along every path: 3 * 2^2 = 12 edges).
4. One dead marking: Jobs={2, 4} Results={1, 9, 25}. Dead but not empty: the guard blocks
   the even jobs forever.
5. Invalid: square<n=2> (guard false) and square<n=7> (no token) raise NotEnabledError;
   a job outside JOB (e.g. 12) is rejected when the place is created (ColourError).
"""

from petrilab.petri.cpn import (
    CPN,
    ColourError,
    ColourSet,
    NotEnabledError,
    dead_markings,
    format_marking,
    var,
)

JOB = ColourSet("JOB", tuple(range(10)))
RESULT = ColourSet("RESULT", tuple(n * n for n in range(10)))


def odd_jobs(jobs: tuple[int, ...] = (1, 2, 3, 4, 5)) -> CPN:
    net = CPN("odd_jobs")
    net.add_place("Jobs", JOB, jobs)
    net.add_place("Results", RESULT)
    net.add_transition(
        "square",
        variables={"n": JOB},
        guard=lambda b: b["n"] % 2 == 1,
        inputs={"Jobs": var("n")},
        outputs={"Results": lambda b: [b["n"] * b["n"]]},
    )
    return net


def check() -> None:
    net = odd_jobs()
    m0 = net.initial_marking
    assert [b["n"] for b in net.enabled_bindings(m0, "square")] == [1, 3, 5]
    graph = net.reachable()
    assert len(graph) == 8
    assert sum(map(len, graph.values())) == 12
    (dead,) = dead_markings(graph)
    assert format_marking(dead) == "Jobs={2, 4} Results={1, 9, 25}"

    for bad in ({"n": 2}, {"n": 7}):
        try:
            net.fire(m0, "square", bad)
        except NotEnabledError:
            pass
        else:
            raise AssertionError(f"{bad} must not be enabled")
    try:
        odd_jobs((12,))
    except ColourError:
        pass
    else:
        raise AssertionError("12 is not in JOB")

    # edge case: duplicate jobs are a multiset: 2`3 fires twice
    twice = odd_jobs((3, 3))
    assert format_marking(twice.initial_marking) == "Jobs={2`3} Results={}"
    (end,) = dead_markings(twice.reachable())
    assert format_marking(end) == "Jobs={} Results={2`9}"


if __name__ == "__main__":
    check()
    print("C1 OK:", format_marking(dead_markings(odd_jobs().reachable())[0]))
