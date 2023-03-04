from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def testing_folder():
    testing_dir = Path("version_api")
    for idx in range(4):
        temp_dir = testing_dir
        temp_path = "../" * idx + "./testing"
        temp_dir = temp_dir.joinpath(temp_path).resolve()
        print(temp_dir)
        if temp_dir.is_dir():
            testing_dir = temp_dir
            break
    else:
        testing_dir = None
    return testing_dir
