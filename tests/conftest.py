from pathlib import Path

import pytest

SAMPLE_ZIP = Path(__file__).resolve().parent / "data" / "sample_export.zip"


@pytest.fixture
def sample_zip_bytes():
    return SAMPLE_ZIP.read_bytes()
