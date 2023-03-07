import pytest

from pyproject_toml_api.version_api.version import Version


def test_version_find(testing_folder):
    version = Version.find(0, pyproject_folder=testing_folder)
    assert str(version) == "0.1.3"


def test_empty_version():
    assert str(Version()) == "0.1.0"


def test_version_repr():
    assert repr(Version()) == "Version('0.1.0')"


@pytest.mark.xfail(reason="not implemented yet")
def test_version_eq():
    # assert True
    assert Version("0.1.1") == Version("0.1.1")


@pytest.mark.parametrize(
    "version_str", ("0.1.0", "v1!3.5.6a1.post6.dev9+windows.1", "1.2.3a1")
)
def test_parameterized_version(version_str):
    version = Version(version_str)
    assert str(version) == version_str


@pytest.mark.parametrize(
    "version_str, expected_str",
    (
        ("0.1.0.a1", "0.1.0a1"),
        (
            "v1!3.5.6-a1.rev6.dev9+windows-1",  # Complex one
            "v1!3.5.6a1.post6.dev9+windows.1",
        ),
        ("1.2.3.a.rev.dev", "1.2.3a0.post0.dev0"),
    ),
)
def test_parameterized_version_normalised(version_str, expected_str):
    version = Version(version_str)
    assert str(version) == expected_str
