"""
version.py



Author: Zack Hankin

Started: 3/03/2023
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from semantic_version import Version


def fetch_version(
    max_folders_up: int = 3,
    pyproject_folder: Optional[str | Path] = None,
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
    elif isinstance(pyproject_folder, str | Path):
        pyproject_folder = Path(pyproject_folder)
    else:
        msg: str = (
            f"pyproject_folder parameter of invalid type: "  # fmt: off
            f"{type(pyproject_folder)}"  # fmt: on
        )
        raise TypeError(msg)
    ret_release: Version = Version(default_version)

    for idx in range(max_folders_up + 1):
        temp_path = "../" * idx + "pyproject.toml"
        pyproject_toml = pyproject_folder.joinpath(temp_path).resolve()
        print(pyproject_toml)
        if pyproject_toml.is_file():
            break
    else:
        raise FileNotFoundError("pyproject.toml not found")

    with open(pyproject_toml, "r") as fin:
        for line in fin.readlines():
            if line.startswith("version"):
                ret_release = Version.coerce(line.split('"')[1])

    if re.match(Version.version_re, default_version):
        return ret_release
    else:
        msg = f"Not a valid semantic version style: {ret_release}"
        raise SyntaxError(msg)
