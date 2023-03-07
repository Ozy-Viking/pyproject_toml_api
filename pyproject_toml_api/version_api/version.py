"""
Python Versioning

As outlined by PEP440:
https://peps.python.org/pep-0440/

[N!]N(.N)*[{a|b|rc}N][.postN][.devN]+[local].N

N: [0-9]
a: alpha version
b: beta version
rc: release candidate number
post: post-release
dev: development version
local: [A-Za-z0-9]*

Author: Zack Hankin

Started: 3/03/2023

Version: v0.1.0
"""
from __future__ import annotations

from pathlib import Path, PurePath
from typing import Optional

from .version_dict import VersionDict
from .version_util import VersionTypeError


class SemanticVersion:
    """
    Ensures that a valid Semantic version is set.
    """

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if isinstance(value, str):
            version_dict = VersionDict.construct(value)
        elif isinstance(value, VersionDict):
            version_dict = value
        else:
            raise VersionTypeError(
                f"Invalid type was given: {type(value).__name__}"  # no fmt
            )
        setattr(instance, self.name, version_dict)


class Version:
    """
    Version
    """

    __slots__: tuple[str, ...] = ("_version_dict", "_version")
    version = SemanticVersion()

    def __init__(self, version: Optional[str] = None) -> None:
        # self._version = SemanticVersion()
        self.version = VersionDict() if version is None else version

    def semantic(self):
        ...

    @property
    def epoch(self) -> Optional[str]:
        return self.version.epoch

    @property
    def major(self) -> str:
        return self.version.major

    @property
    def minor(self) -> str:
        return self.version.minor

    @property
    def patch(self) -> str:
        return self.version.patch

    @property
    def prerelease(self) -> Optional[str]:
        return f"{self.version.pre_l}{self.version.pre_n}"

    @property
    def postrelease(self) -> Optional[str]:
        if self.version.post_n1 is not None:
            return self.version.post_n1
        if (
            self.version.post_l is None  # fmt: ignore
            or self.version.post_n2 is None  # fmt: ignore
        ):
            return None
        return f"{self.version.post_l}{self.version.post_n2}"

    @property
    def developmentrelease(self) -> Optional[str]:
        return f"{self.version.dev_l}{self.version.dev_n}"

    @property
    def localversion(self) -> Optional[str]:
        return f"{self.version.local_l}.{self.version.local_n}"

    def __str__(self) -> str:
        """
        Version string.

        Returns:
            str: Version string i.e. '1!1.3c4.dev3'
        """
        return str(self.version)

    def __repr__(self) -> str:
        """
        Return the representation of the object.

        Returns:
            str: Representation of the object i.e. Version("1!1.3c4.dev3")
        """
        return f"{type(self).__name__}('{str(self)}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return other == self
        elif isinstance(other, str):
            other = other[1:] if other.casefold().startswith("v") else other
            self_str = str(self)
            self_str = (
                self_str[1:]  # fmt: ignore
                if self_str.casefold().startswith("v")  # fmt: ignore
                else self_str  # fmt: ignore
            )
            return self_str == other
        else:
            return NotImplemented

    @classmethod
    def find(
        cls,
        max_folders_up: int = 10,
        pyproject_folder: Optional[Path] = None,
        default_version: str = "0.1.0",
    ) -> Version:
        """
        Fetches the version number for the pyproject.toml up
        to the max folders up.

        Args:
            pyproject_folder (Optional[str | Path]): Set the path if known.
            max_folders_up (int): Max number of folders up to search.
                                  0 is the given folder.
            default_version (str): If no version is found, what version
                                   do you want returned.

        Returns:
            Version: Version for the project ensuring PEP440 compliance.

        Raises:
            TypeError:
            FileNotFoundError:
            SyntaxError:

        todo: finish this.
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
