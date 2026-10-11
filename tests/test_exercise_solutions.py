"""Every exercise solution in exercises/solutions/ passes its own check()."""

import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "exercises"
SOLUTIONS = sorted((ROOT / "solutions").glob("*.py"))


@pytest.mark.parametrize("solution", SOLUTIONS, ids=lambda p: p.stem)
def test_solution_checks(solution: Path) -> None:
    namespace = runpy.run_path(str(solution))  # does not trigger the __main__ block
    namespace["check"]()


def test_every_solution_has_a_statement() -> None:
    statements = {p.stem.split("-")[0] for p in ROOT.glob("*/*.md")}
    solutions = {p.stem.split("_")[0] for p in SOLUTIONS}
    assert solutions == statements - {"README"}
