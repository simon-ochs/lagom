"""Characterization test for the analysis algorithm.

It pins down what the code currently does so unintended changes surface as a diff.

`run_analysis` is deterministic given a fixed input, so we snapshot its full
output and diff against it. When you intentionally change the algorithm and the
numbers move, re-bless the snapshot:

    UPDATE_SNAPSHOT=1 pytest tests/test_analysis.py

then review the diff in tests/snapshots/expected.json before committing.
"""
import json
import os
from pathlib import Path

from app import analysis, loader
from app.models import PumpConfig

SNAPSHOT = Path(__file__).resolve().parent / "snapshots" / "expected.json"

# Fixed config so the baseline never depends on defaults drifting.
CONFIG = PumpConfig(icr=10, isf=30, target_glucose=110)


def _run(sample_zip_bytes):
    frames = loader.load_glooko_zip(sample_zip_bytes)
    result = analysis.run_analysis(*frames, CONFIG)
    # Round-trip through JSON so the comparison matches what the API returns.
    return json.loads(json.dumps(result))


def test_analysis_matches_snapshot(sample_zip_bytes):
    result = _run(sample_zip_bytes)

    if os.environ.get("UPDATE_SNAPSHOT"):
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(result, indent=2) + "\n")

    expected = json.loads(SNAPSHOT.read_text())
    assert result == expected
