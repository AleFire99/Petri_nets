import pytest
from statemachine.exceptions import TransitionNotAllowed

from petrilab.fsm.extended import VendingMachine


def state(sm: VendingMachine) -> str:
    return next(iter(sm.configuration)).id


def test_underfunded_select_rejected() -> None:
    sm = VendingMachine()
    sm.send("insert", amount=50)
    sm.send("select")
    assert (state(sm), sm.credit, sm.dispensed, sm.rejected) == ("has_credit", 50, 0, 1)


def test_exact_payment_returns_to_idle() -> None:
    sm = VendingMachine()
    sm.send("insert", amount=75)
    sm.send("select")
    assert (state(sm), sm.credit, sm.dispensed) == ("idle", 0, 1)


def test_change_retained_after_purchase() -> None:
    sm = VendingMachine()
    sm.send("insert", amount=100)
    sm.send("select")
    assert (state(sm), sm.credit, sm.dispensed) == ("has_credit", 25, 1)


def test_credit_accumulates_and_refund_zeroes() -> None:
    sm = VendingMachine()
    sm.send("insert", amount=25)
    sm.send("insert", amount=25)
    assert sm.credit == 50
    sm.send("refund")
    assert (state(sm), sm.credit) == ("idle", 0)


def test_non_positive_insert_rejected() -> None:
    sm = VendingMachine()
    with pytest.raises(TransitionNotAllowed):
        sm.send("insert", amount=0)
    assert sm.credit == 0


def test_select_when_idle_invalid() -> None:
    with pytest.raises(TransitionNotAllowed):
        VendingMachine().send("select")
