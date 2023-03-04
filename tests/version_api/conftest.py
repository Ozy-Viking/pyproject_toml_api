from pathlib import Path

import pytest


@pytest.fixture
def testing_folder():
    testing_dir = Path("../../pyproject_toml_api")
    for idx in range(2):
        temp_path = "../" * idx + "testing"
        testing_dir = testing_dir.joinpath(temp_path).resolve()
        if testing_dir.is_dir():
            break
    else:
        testing_dir = None
    return testing_dir
