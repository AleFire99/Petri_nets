"""Cross-formalism check: XState EFSM vs Petri net for the dining philosophers.

xstate/src/machines/philosophers.machine.ts models each philosopher as a parallel
region and forks as context variables. Its exhaustive exploration
(xstate/generated/reports/philosophers-*.json) must give the same reachability
graph size and the same dead states as the Petri net in examples.py.
"""

import json
from pathlib import Path

import pytest

from petrilab.petri import examples

REPORTS = Path(__file__).resolve().parents[2] / "xstate" / "generated" / "reports"


@pytest.mark.parametrize("n_phil", [2, 3, 4])
@pytest.mark.parametrize("atomic", [False, True], ids=["naive", "atomic"])
def test_xstate_and_petri_agree(n_phil: int, atomic: bool) -> None:
    slug = f"philosophers-{n_phil}-{'atomic' if atomic else 'naive'}"
    report = json.loads((REPORTS / f"{slug}.json").read_text())
    graph = examples.dining_philosophers(n_phil, atomic=atomic).reachable()

    assert report["stateCount"] == len(graph)
    assert report["edgeCount"] == sum(len(succ) for succ in graph.values())
    assert len(report["deadlocks"]) == sum(1 for succ in graph.values() if not succ)


@pytest.mark.parametrize("n_phil", [2, 3, 4])
def test_xstate_deadlock_trace_fires_in_petri_net(n_phil: int) -> None:
    """The counterexample XState prints is a valid firing sequence to a dead marking."""
    report = json.loads((REPORTS / f"philosophers-{n_phil}-naive.json").read_text())
    (deadlock,) = report["deadlocks"]
    net = examples.dining_philosophers(n_phil)
    m = net.initial_marking
    for t in deadlock["trace"]:
        m = net.fire(m, t)
    assert net.enabled_transitions(m) == []
