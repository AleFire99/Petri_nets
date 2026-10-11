"""Vending machine EFSM on the generic engine (design: docs/fsm/extended.md).

Model: xstate/src/machines/vendingMachine.machine.ts. Same state ids, context names and
transition order, so tests/fsm/test_vending_machine.py replays
xstate/generated/vectors/vending-machine.json and compares the exploration counts with
xstate/generated/reports/vending-machine.json.
"""

from collections.abc import Mapping
from typing import Any

from petrilab.fsm.efsm import EFSM, Context, Event, Transition

PRICE = 75


# Guards: pure predicates on (context, event)
def positive(ctx: Context, ev: Event) -> bool:
    return int(ev.get("amount", 0)) > 0


def exact(ctx: Context, ev: Event) -> bool:
    return bool(ctx["credit"] == PRICE)


def enough(ctx: Context, ev: Event) -> bool:
    return bool(ctx["credit"] >= PRICE)


# Actions: return only the updated variables
def add_credit(ctx: Context, ev: Event) -> Mapping[str, Any]:
    return {"credit": ctx["credit"] + ev["amount"]}


def dispense(ctx: Context, ev: Event) -> Mapping[str, Any]:
    return {"credit": ctx["credit"] - PRICE, "dispensed": ctx["dispensed"] + 1}


def reject(ctx: Context, ev: Event) -> Mapping[str, Any]:
    return {"rejected": ctx["rejected"] + 1}


def clear_credit(ctx: Context, ev: Event) -> Mapping[str, Any]:
    return {"credit": 0}


def vending_machine() -> EFSM:
    return EFSM(
        "vendingMachine",
        states=("idle", "has_credit"),
        initial="idle",
        context={"credit": 0, "dispensed": 0, "rejected": 0},
        transitions=[
            # declaration order = priority, as in the XState `select` array
            Transition("idle", "insert", "has_credit", positive, add_credit,
                       "[amount > 0] / credit += amount"),
            Transition("has_credit", "insert", "has_credit", positive, add_credit,
                       "[amount > 0] / credit += amount"),
            Transition("has_credit", "select", "idle", exact, dispense,
                       "[credit == price] / dispense"),
            Transition("has_credit", "select", "has_credit", enough, dispense,
                       "[credit >= price] / dispense"),
            Transition("has_credit", "select", "has_credit", None, reject,
                       "[else] / rejected += 1"),
            Transition("has_credit", "refund", "idle", None, clear_credit,
                       "/ credit = 0"),
        ],
    )  # fmt: skip


COINS: tuple[int, ...] = (0, 25, 50, 100)
"""Payload variants used by the XState spec (``vendingSpec`` in designs.checks.ts)."""


def environment_events(coins: tuple[int, ...] = COINS) -> list[Event]:
    """Every event the environment can send: one ``insert`` per coin, ``select``, ``refund``."""
    return [
        *({"type": "insert", "amount": c} for c in coins),
        {"type": "select"},
        {"type": "refund"},
    ]
