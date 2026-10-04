import pytest

from petrilab.fsm.timed import DoorAlarm


def test_no_alarm_before_timeout() -> None:
    d = DoorAlarm()
    d.send("open")
    d.advance(29)
    assert d.state == "open"


def test_alarm_at_timeout() -> None:
    d = DoorAlarm()
    d.send("open")
    d.advance(30)
    assert d.state == "alarm"


def test_close_cancels_timer() -> None:
    d = DoorAlarm()
    d.send("open")
    d.advance(20)
    d.send("close")
    d.advance(100)
    assert d.state == "closed"


def test_reopen_restarts_timer() -> None:
    d = DoorAlarm()
    d.send("open")
    d.advance(20)
    d.send("close")
    d.send("open")
    d.advance(20)
    assert d.state == "open"
    d.advance(10)
    assert d.state == "alarm"


def test_close_from_alarm() -> None:
    d = DoorAlarm()
    d.send("open")
    d.advance(31)
    d.send("close")
    assert d.state == "closed"


def test_unknown_event() -> None:
    with pytest.raises(ValueError):
        DoorAlarm().send("kick")
