from pathlib import Path

import pytest


@pytest.fixture
def testing_folder():
    return Path(__file__).joinpath("../../testing").resolve()
