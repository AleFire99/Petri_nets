"""Replay the XState model's test vectors against the hand-written FillStation.

Vectors come from `npm run export` in fsm/xstate/ (committed as
fsm/xstate/generated/vectors/fill-station.json): one vector per transition of the
verified model; each step states the expected state, Moore outputs and context.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from petrilab.fsm.fill_station import FillStation

VECTORS = (
    Path(__file__).resolve().parents[2]
    / "fsm"
    / "xstate"
    / "generated"
    / "vectors"
    / "fill-station.json"
)


def vectors() -> list[dict[str, Any]]:
    vs: list[dict[str, Any]] = json.loads(VECTORS.read_text())["vectors"]
    return vs


@pytest.mark.parametrize("vector", vectors(), ids=lambda v: str(v["id"]))
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


def test_unknown_event_is_ignored() -> None:
    fs = FillStation()
    fs.send("KICK")
    assert fs.state == "idle"
