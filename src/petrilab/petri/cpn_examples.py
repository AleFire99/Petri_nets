"""CPNs from docs/petri/cpn-formal.md, built with the hand-written engine in ``cpn.py``.

Each one folds a P/T net from ``examples.py`` (or the SNAKES net in ``colored.py``), so the
tests can check that both formalisms give the same state space.
"""

from petrilab.petri.cpn import CPN, UNIT, Binding, ColourSet, const, var

INT_0_9 = ColourSet("INT0..9", tuple(range(10)))


def jobs(job_values: tuple[int, ...] = (1, 2, 3)) -> CPN:
    """``square`` consumes a job ``n`` if ``n > 1`` and produces ``n*n`` (colored.md)."""
    results = ColourSet("RESULT", tuple(n * n for n in range(10)))
    net = CPN("jobs")
    net.add_place("Jobs", INT_0_9, job_values)
    net.add_place("Results", results)
    net.add_transition(
        "square",
        variables={"n": INT_0_9},
        guard=lambda b: b["n"] > 1,
        inputs={"Jobs": var("n")},
        outputs={"Results": lambda b: [b["n"] * b["n"]]},
    )
    return net


def philosophers(n_phil: int = 3, *, atomic: bool = False) -> CPN:
    """Dining philosophers folded: one place per *role*, philosophers and forks as colours.

    Philosopher ``p`` uses forks ``p`` (left) and ``(p + 1) % n`` (right), as in
    ``examples.dining_philosophers``. Unfolding gives exactly that P/T net.
    """
    if n_phil < 2:
        raise ValueError("need at least two philosophers")
    ph = ColourSet("PH", tuple(range(n_phil)))
    fk = ColourSet("FK", tuple(range(n_phil)))

    def right(b: Binding) -> list[int]:
        return [(b["p"] + 1) % n_phil]

    net = CPN(f"philosophers_cpn_{n_phil}_{'atomic' if atomic else 'naive'}")
    net.add_place("Think", ph, ph.values)
    net.add_place("Fork", fk, fk.values)
    net.add_place("Eat", ph)
    p = {"p": ph}
    if atomic:
        net.add_transition(
            "take",
            variables=p,
            inputs={"Think": var("p"), "Fork": lambda b: [b["p"], *right(b)]},
            outputs={"Eat": var("p")},
        )
    else:
        net.add_place("HasLeft", ph)
        net.add_transition(
            "takeLeft",
            variables=p,
            inputs={"Think": var("p"), "Fork": var("p")},
            outputs={"HasLeft": var("p")},
        )
        net.add_transition(
            "takeRight",
            variables=p,
            inputs={"HasLeft": var("p"), "Fork": right},
            outputs={"Eat": var("p")},
        )
    net.add_transition(
        "done",
        variables=p,
        inputs={"Eat": var("p")},
        outputs={"Think": var("p"), "Fork": lambda b: [b["p"], *right(b)]},
    )
    return net


def mutex(n_proc: int = 2) -> CPN:
    """``n_proc`` processes share one lock (folds ``examples.mutex`` for ``n_proc = 2``)."""
    proc = ColourSet("PROC", tuple(range(1, n_proc + 1)))
    net = CPN(f"mutex_cpn_{n_proc}")
    net.add_place("Mutex", UNIT, [()])
    net.add_place("Idle", proc, proc.values)
    net.add_place("Wait", proc)
    net.add_place("Crit", proc)
    i = {"i": proc}
    net.add_transition(
        "request", variables=i, inputs={"Idle": var("i")}, outputs={"Wait": var("i")}
    )
    net.add_transition(
        "enter",
        variables=i,
        inputs={"Wait": var("i"), "Mutex": const(())},
        outputs={"Crit": var("i")},
    )
    net.add_transition(
        "leave",
        variables=i,
        inputs={"Crit": var("i")},
        outputs={"Idle": var("i"), "Mutex": const(())},
    )
    return net
