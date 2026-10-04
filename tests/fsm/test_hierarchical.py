import pytest
from statemachine.exceptions import TransitionNotAllowed

from petrilab.fsm.hierarchical import MediaPlayer


def ids(sm: MediaPlayer) -> set[str]:
    return {s.id for s in sm.configuration}


def test_power_on_enters_stopped() -> None:
    sm = MediaPlayer()
    sm.send("power_on")
    assert ids(sm) == {"on", "stopped"}


@pytest.mark.parametrize("path", [[], ["play"], ["play", "pause"]])
def test_power_off_from_any_child(path: list[str]) -> None:
    sm = MediaPlayer()
    sm.send("power_on")
    for e in path:
        sm.send(e)
    sm.send("power_off")
    assert ids(sm) == {"off"}


def test_play_while_off_invalid() -> None:
    with pytest.raises(TransitionNotAllowed):
        MediaPlayer().send("play")


def test_reentering_starts_stopped() -> None:
    sm = MediaPlayer()
    sm.send("power_on")
    sm.send("play")
    sm.send("power_off")
    sm.send("power_on")
    assert ids(sm) == {"on", "stopped"}


def test_pause_resume_stop() -> None:
    sm = MediaPlayer()
    for e in ("power_on", "play", "pause", "play", "stop"):
        sm.send(e)
    assert ids(sm) == {"on", "stopped"}
