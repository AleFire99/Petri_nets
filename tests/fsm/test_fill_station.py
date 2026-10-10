"""Replay XState-generated test vectors against the Python implementations.

Vectors come from `npm run export` in xstate/ (committed under xstate/generated/).
Each vector is a path through the verified model; every step states the expected
leaf state, Moore outputs and context. One vector per explored transition.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from petrilab.fsm.extended import VendingMachine
from petrilab.fsm.fill_station import FillStation
from petrilab.fsm.timed import DoorAlarm

GENERATED = Path(__file__).resolve().parents[2] / "xstate" / "generated"


def vectors(slug: str) -> list[dict[str, Any]]:
    data = json.loads((GENERATED / slug / "vectors.json").read_text())
    vs: list[dict[str, Any]] = data["vectors"]
    return vs


def ids(v: dict[str, Any]) -> str:
    return str(v["id"])


@pytest.mark.parametrize("vector", vectors("fill-station"), ids=ids)
def test_fill_station_matches_model(vector: dict[str, Any]) -> None:
    fs = FillStation()
    for step in vector["steps"]:
        if "wait" in step:
            fs.tick(step["wait"])
        else:
            fs.send(step["event"]["type"])
        exp = step["expect"]
        assert [fs.state] == exp["state"], step
        assert sorted(fs.outputs) == exp["outputs"], step
        assert {"retries": fs.retries, "lastFault": fs.last_fault} == exp["context"]


@pytest.mark.parametrize("vector", vectors("door-alarm"), ids=ids)
def test_door_alarm_matches_model(vector: dict[str, Any]) -> None:
    door = DoorAlarm()
    for step in vector["steps"]:
        if "wait" in step:
            door.advance(step["wait"] / 1000)  # model in ms, sismic in s
        else:
            door.send(step["event"]["type"])
        assert [door.state] == step["expect"]["state"], step


@pytest.mark.parametrize("vector", vectors("vending-machine"), ids=ids)
def test_vending_machine_matches_model(vector: dict[str, Any]) -> None:
    sm = VendingMachine()
    for step in vector["steps"]:
        event = dict(step["event"])
        sm.send(event.pop("type"), **event)
        state = next(iter(sm.configuration)).id
        ctx = {"credit": sm.credit, "dispensed": sm.dispensed, "rejected": sm.rejected}
        assert [state] == step["expect"]["state"], step
        assert ctx == step["expect"]["context"], step
