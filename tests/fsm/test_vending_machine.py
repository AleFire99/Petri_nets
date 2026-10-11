"""Vending machine on the Python EFSM engine, proven against the XState model.

- vectors: xstate/generated/vectors/vending-machine.json (one per explored transition)
- report:  xstate/generated/reports/vending-machine.json (state/edge counts, depth 4)
"""

import json
from pathlib import Path
from typing import Any

import pytest

from petrilab.fsm.efsm import Configuration, InvalidTransitionError, Machine, explore
from petrilab.fsm.vending_machine import PRICE, environment_events, vending_machine

GENERATED = Path(__file__).resolve().parents[2] / "xstate" / "generated"


def vectors() -> list[dict[str, Any]]:
    vs: list[dict[str, Any]] = json.loads(
        (GENERATED / "vectors" / "vending-machine.json").read_text()
    )["vectors"]
    return vs


def test_initial_matches_model() -> None:
    initial = json.loads((GENERATED / "vectors" / "vending-machine.json").read_text())[
        "initial"
    ]
    m = Machine(vending_machine())
    assert [m.state] == initial["state"] and m.context == initial["context"]


@pytest.mark.parametrize("vector", vectors(), ids=lambda v: str(v["id"]))
def test_vending_machine_matches_model(vector: dict[str, Any]) -> None:
    m = Machine(vending_machine())
    for step in vector["steps"]:
        m.send(step["event"])
        exp = step["expect"]
        assert [m.state] == exp["state"], step
        assert exp["outputs"] == []  # no Moore outputs in this design
        assert m.context == exp["context"], step


def test_exploration_counts_match_xstate_report() -> None:
    report = json.loads((GENERATED / "reports" / "vending-machine.json").read_text())
    r = explore(vending_machine(), environment_events(), max_depth=4)
    assert r.state_count == report["stateCount"]
    assert r.edge_count == report["edgeCount"]
    assert len(r.deadlocks()) == len(report["deadlocks"])


def test_invariants_hold_on_explored_space() -> None:
    r = explore(vending_machine(), environment_events(), max_depth=5)
    invariants = {
        "credit never negative": lambda c: c.ctx["credit"] >= 0,
        "idle means no credit": lambda c: c.state != "idle" or c.ctx["credit"] == 0,
        "has_credit means credit > 0": lambda c: c.state != "has_credit" or c.ctx["credit"] > 0,
    }  # fmt: skip
    assert r.violations(invariants) == []


# -- scenarios: normal, edge, invalid -------------------------------------------------------
def test_exact_purchase_returns_to_idle() -> None:
    m = Machine(vending_machine())
    m.send("insert", amount=50)
    m.send("insert", amount=25)
    m.send("select")
    assert m.config == Configuration.of(
        "idle", {"credit": 0, "dispensed": 1, "rejected": 0}
    )


def test_change_is_kept_after_purchase() -> None:
    m = Machine(vending_machine())
    m.send("insert", amount=100)
    m.send("select")
    assert m.state == "has_credit" and m.context["credit"] == 100 - PRICE


def test_underfunded_select_is_rejected() -> None:
    m = Machine(vending_machine())
    m.send("insert", amount=50)
    m.send("select")
    assert m.state == "has_credit"
    assert m.context == {"credit": 50, "dispensed": 0, "rejected": 1}


def test_zero_coin_is_ignored() -> None:
    m = Machine(vending_machine())
    assert m.send("insert", amount=0) is False
    assert m.state == "idle"


def test_select_in_idle_is_invalid_in_strict_mode() -> None:
    m = Machine(vending_machine(), strict=True)
    with pytest.raises(InvalidTransitionError):
        m.send("select")
    with pytest.raises(InvalidTransitionError):
        m.send("refund")
