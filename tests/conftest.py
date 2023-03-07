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
        return None
    return testing_dir


@pytest.fixture
def deep_path_testing_folder(testing_folder):
    return testing_folder.joinpath("a/b/c/d/e/f")
