from semantic_version import Version

from pyproject_toml_api.version_api.version import fetch_version


def test_current_version(testing_folder):
    version = fetch_version(0, pyproject_folder=testing_folder)
    assert version == Version("0.1.3")
