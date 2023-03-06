"""
version.py

[N!]N(.N)*[{a|b|rc}N][.postN][.devN]

Author: Zack Hankin

Started: 3/03/2023
"""
from __future__ import annotations

import re
from pathlib import Path, PurePath
from typing import Optional

from icecream import ic

VERSION_PATTERN: str = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?:  #P<release>                                      # release
            (?P<major>[0-9]+)
            (?:\.(?P<minor>[0-9]+))?
            (?:\.(?P<patch>[0-9]+))?
            )
        (?:  #P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?:  #P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?: # P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?:  #P<local>
        (?P<local_l>[a-z0-9]+)
        (?:[-_\.]
        (?P<local_n>[a-z0-9]+))*)
        )?       # local version
"""

VERSION_REGEX = re.compile(
    r"^\s*" + VERSION_PATTERN + r"\s*$",
    re.VERBOSE | re.IGNORECASE,
)
VERSION_INT_KEYS = {
    "epoch",
    "major",
    "minor",
    "patch",
    "pre_n",
    "post_n1",
    "post_n2",
    "dev_n",
}

VERSION_IMPLICIT_KEYS = {
    ("pre_l", "pre_n"),
    ("post_l", "post_n2"),
    ("dev_l", "dev_n"),
}

VERSION_KEYS = [
    "epoch",
    "major",
    "minor",
    "patch",
    "pre_l",
    "pre_n",
    "post_n1",
    "post_l",
    "post_n2",
    "dev_l",
    "dev_n",
    "local_l",
    "local_n",
]
VERSION_LABELS = [
    "pre_l",
    "post_l",
    "dev_l",
    "local_l",
]
VERSION_DOTTED_SEGMENT = {
    "minor",
    "patch",
    "post_n1",
    "dev_l",
    "local_n",
}


def casefold_version(version: Optional[re.Match | str]) -> Optional[re.Match]:
    """
    Changes the version letter case to lowercase, inline with PEP440.

    Parameters:
        version (Optional[re.Match|str]): Version string or matched object. If
                                          string is given, it will be matched
                                          against the regex for versioning.

    Returns:
        Optional[re.Match]: Matched version object or None if no match.
    """
    if version is None:
        return version
    elif isinstance(version, str):
        version_str = version.casefold().strip()
    elif isinstance(version, re.Match):
        version_str = version.string.casefold()
    else:
        raise TypeError(f"Invalid version type: {type(version).__name__}")
    return VERSION_REGEX.match(version_str)


def remove_leading_zeros(
    version: Optional[re.Match | str],
) -> Optional[re.Match]:
    """
    Remove leading zeroes from any integer.

    Args:
        version (Optional[re.Match | str]):

    Returns:
        Optional[re.Match]:
    """
    if isinstance(version, str):
        version = VERSION_REGEX.match(version)
    if version is None:
        return version

    version_dict = version.groupdict()
    for key, value in version_dict.items():
        if value is not None and (key in VERSION_INT_KEYS):
            version_dict[key] = str(int(value))
    version_str: str = construct_valid_version_from_dict(version_dict)
    return VERSION_REGEX.match(version_str)


def construct_valid_version_from_dict(version_dict: dict[str, str]) -> str:
    """
    Constructs a valid version string from a dictionary of keys from version
    regex.

    Args:
        version_dict (dict[str, str]): Keys from VERSION_KEYS.

    Returns:
        str: A valid version string.
    """
    ret_version = ""
    for key in VERSION_KEYS:
        if version_dict[key] is None:
            continue
        if key == "epoch":
            ret_version += version_dict[key] + "!"
            continue
        elif key == "local_l":
            ret_version += "+" + version_dict[key]
            continue
        elif key in VERSION_DOTTED_SEGMENT:
            ret_version += "." + version_dict[key]
        elif key == "post_l":
            ret_version += ".post"
        elif key in VERSION_KEYS:
            ret_version += version_dict[key]
        else:
            raise KeyError(f"Unexpected key: {key}")
    return ret_version


def normalise_labels(version):
    if version is None:
        return version
    elif isinstance(version, str):
        version = VERSION_REGEX.match(version)
    elif not isinstance(version, re.Match):
        raise TypeError(f"Unexpected version type: {type(version).__name__}")

    version_dict = version.groupdict()

    for key in ["pre_l", "post_l", "post_n1"]:
        temp_value = version_dict[key]
        if temp_value is None:
            continue
        if key == "pre_l":
            if temp_value in ["a", "alpha"]:
                version_dict[key] = "a"
            elif temp_value in ["b", "beta"]:
                version_dict[key] = "b"
            elif temp_value in ["c", "rc", "pre", "preview"]:
                version_dict[key] = "rc"
        elif key == "post_l":
            version_dict[key] = "post"
        elif key == "post_n1":
            version_dict[key] = f"post{temp_value}"
    version_str: str = construct_valid_version_from_dict(version_dict)
    return VERSION_REGEX.match(version_str)


def add_explicit_zeros(version):
    if version is None:
        return version
    elif isinstance(version, str):
        version = VERSION_REGEX.match(version)
    elif not isinstance(version, re.Match):
        raise TypeError(f"Unexpected version type: {type(version).__name__}")

    version_dict = version.groupdict()

    for key1, key2 in VERSION_IMPLICIT_KEYS:
        if version_dict[key1] and not version_dict[key2]:
            version_dict[key2] = "0"

    version_str = construct_valid_version_from_dict(version_dict)

    return VERSION_REGEX.match(version_str)


def normalise_version(
    version: Optional[re.Match | str],
) -> Optional[re.Match]:
    if version is None:
        return version
    if isinstance(version, str):
        version = VERSION_REGEX.match(version)
    ret_version: Optional[re.Match] = version
    ret_version = normalise_labels(ret_version)
    ret_version = casefold_version(ret_version)
    ret_version = remove_leading_zeros(ret_version)
    ret_version = add_explicit_zeros(ret_version)
    return ret_version


class SemanticVersion:
    """
    Ensures that a valid Semantic version is set.
    """

    def __init__(self):
        self.name: str

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __set__(self, instance, value):
        if value := VERSION_REGEX.match(value):
            value = normalise_version(value)
            instance.__dict__ |= value.groupdict()
        else:
            msg: str = "Version does not match valid Semantic versioning."
            raise AttributeError(msg)


class Version:
    """
    Version
    """

    version = SemanticVersion()

    def __init__(self, version: Optional[str] = None) -> None:
        self.version = version if version else fetch_version()

    @property
    def epoch(self) -> str:
        return self.__dict__["epoch"]

    @property
    def major(self) -> str:
        return self.__dict__["major"]

    @property
    def minor(self) -> str:
        return self.__dict__["minor"]

    @property
    def patch(self) -> str:
        return self.__dict__["patch"]

    @property
    def prerelease(self) -> Optional[str]:
        return f'{self.__dict__["pre_l"]}{self.__dict__["pre_n"]}'

    @property
    def postrelease(self) -> Optional[str]:
        if self.__dict__["post_n1"] is not None:
            return self.__dict__["post_n1"]
        if (
            self.__dict__["post_l"] is None  # fmt: ignore
            or self.__dict__["post_n2"] is None  # fmt: ignore
        ):
            return None
        return f'{self.__dict__["post_l"]}{self.__dict__["post_n2"]}'

    @property
    def developmentrelease(self) -> Optional[str]:
        return f'{self.__dict__["dev_l"]}{self.__dict__["dev_n"]}'

    @property
    def localversion(self) -> Optional[str]:
        return f'{self.__dict__["local_l"]}.{self.__dict__["local_n"]}'

    def __str__(self) -> str:
        """
        Version string.

        Returns:
            str: Version string i.e. '1!1.3c4.dev3'
        """
        version_dict = {
            key: value
            for (key, value) in self.__dict__.items()  # fmt: ignore
            if key in VERSION_KEYS  # fmt: ignore
        }
        return construct_valid_version_from_dict(version_dict)

    def __repr__(self) -> str:
        """
        Return the representation of the object.

        Returns:
            str: Representation of the object i.e. Version("1!1.3c4.dev3")
        """
        return f'{type(self).__name__}("{str(self)}")'


checker = Version("v1!1.3.785C4.rev3.DEV9+WINDOWS-34")
ic(checker.epoch)
ic(checker.major)
ic(checker.minor)
ic(checker.patch)
ic(checker.prerelease)
ic(checker.postrelease)
ic(checker.developmentrelease)
ic(checker.localversion)


def fetch_version(
    max_folders_up: int = 10,
    pyproject_folder: Optional[Path] = None,
    default_version: str = "0.1.0",
) -> Version:
    """
    Fetches the version number for the pyproject.toml
    folder no more than 2 up.

    Args:
        pyproject_folder (Optional[str | Path]): Set the path if known.
        max_folders_up (int): Max number of folders up to search.
                              0 is the given folder.
        default_version (str): If no version is found, what version
                               do you want returned.

    Returns:
        str: Release and Version number for project,
             using the semantic version style. E.g. "0.1.1"
    """

    if pyproject_folder is None:
        pyproject_folder = Path(__file__).joinpath("../").resolve()
    elif isinstance(pyproject_folder, str):
        pyproject_folder = Path(pyproject_folder)
    elif isinstance(pyproject_folder, PurePath):
        pyproject_folder = Path(pyproject_folder)
    else:
        msg: str = (
            f"pyproject_folder parameter of invalid type: "  # fmt: off
            f"{type(pyproject_folder)}"  # fmt: on
        )
        raise TypeError(msg)
    ret_release: Version = Version(default_version)

    for idx in range(max_folders_up + 1):
        temp_folder = pyproject_folder
        temp_path = "../" * idx + "./pyproject.toml"
        temp_toml: Path = temp_folder.joinpath(temp_path).resolve()
        if temp_toml.is_file():
            pyproject_toml = temp_toml
            break
    else:
        raise FileNotFoundError("pyproject.toml not found")

    with open(pyproject_toml, "r") as fin:
        for line in fin.readlines():
            if line.startswith("version"):
                ret_release = Version(line.split('"')[1])

    if ret_release:
        return ret_release
    else:
        msg = f"Not a valid semantic version style: {ret_release}"
        raise SyntaxError(msg)
