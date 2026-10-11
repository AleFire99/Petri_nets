"""Every script in examples/ runs and prints exactly examples/expected/<name>.txt.

After an intended change, regenerate the expected output:
    UPDATE_EXPECTED=1 uv run pytest tests/test_example_scripts.py
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
SCRIPTS = sorted(EXAMPLES.glob("*.py"))


def test_every_script_has_expected_output() -> None:
    expected = {p.stem for p in (EXAMPLES / "expected").glob("*.txt")}
    assert {s.stem for s in SCRIPTS} == expected


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_example_output(script: Path) -> None:
    run = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=True,
    )
    expected_file = EXAMPLES / "expected" / f"{script.stem}.txt"
    if os.environ.get("UPDATE_EXPECTED"):
        expected_file.write_text(run.stdout)
    assert run.stdout == expected_file.read_text()
