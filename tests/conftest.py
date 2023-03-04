from pathlib import Path

import pytest


@pytest.fixture
def testing_folder():
    return Path("testing").resolve()
