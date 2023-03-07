"""
version_dict.py



Author: Zack Hankin

Started: 7/03/2023
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from version_api.version_util import (
    VERSION_DOTTED_SEGMENT,
    VERSION_IMPLICIT_KEYS,
    VERSION_INT_KEYS,
    VERSION_KEYS,
    VERSION_REGEX,
    VersionKeyError,
    VersionSyntaxError,
)


@dataclass(eq=True)
class VersionDict:
    """
    Version dictionary named tuple.
    """

    v: Optional[str] = field(default=None)
    epoch: Optional[str] = field(default=None)
    major: str = field(default="0")
    minor: str = field(default="1")
    patch: str = field(default="0")
    pre_l: Optional[str] = field(default=None)
    pre_n: Optional[str] = field(default=None)
    post_n1: Optional[str] = field(default=None)
    post_l: Optional[str] = field(default=None)
    post_n2: Optional[str] = field(default=None)
    dev_l: Optional[str] = field(default=None)
    dev_n: Optional[str] = field(default=None)
    local_l: Optional[str] = field(default=None)
    local_n: Optional[str] = field(default=None)

    def __post_init__(self):
        self.normalise_labels()
        self.casefold()
        self.remove_leading_zeros()
        self.add_implicit_zeros()

    @classmethod
    def construct(
        cls,
        version: Optional[str] = None,
        default_version: str = "0.1.0",
    ) -> VersionDict:
        """
        Match a given string and construct a VersionDict instance.

        Args:
            version (str): A python acceptable string representing a version
                           according to PEP440
            default_version (str): The default version that is returned if
                                   version is empty.

        Returns:
            VersionDict: A VersionDict instance

        Raises:
            VersionSyntaxError: When a non-valid version is passed in.
        """
        version_match: Optional[re.Match] = VERSION_REGEX.match(version)
        ret_version: dict[str, str]
        if version is None:
            ret_version = VERSION_REGEX.match(default_version).groupdict()
        elif version.casefold() == "v":
            version_match = VERSION_REGEX.match("v" + default_version)
            if version_match is not None:
                ret_version = version_match.groupdict()
            else:
                raise RuntimeError
        elif isinstance(version_match, re.Match):
            ret_version = version_match.groupdict()
        else:
            error_msg: str = (
                f"Non valid python semantic version was "  # fmt: ignore
                f"given: {version}"  # fmt: ignore
            )
            raise VersionSyntaxError(error_msg)
        return VersionDict(**ret_version)

    def casefold(self) -> VersionDict:
        """
        Changes the version letter case to lowercase, inline with PEP440.

        Returns:
            VersionDict: VersionDict with every part case-folded.
        """
        for key in VERSION_KEYS:
            if (tempattr := getattr(self, key)) is not None:
                setattr(self, key, tempattr)
        return self

    def remove_leading_zeros(self) -> VersionDict:
        """
        Remove leading zeroes from any integer.

        Returns:
            VersionDict: self
        """
        for key in VERSION_INT_KEYS:
            tempattr = getattr(self, key, None)
            if tempattr is not None and (key in VERSION_INT_KEYS):
                setattr(self, key, str(int(tempattr)))
        return self

    def normalise_labels(self) -> VersionDict:
        """
        Normalise version labels to be inline PEP440.

        Returns:
            VersionDict: VersionDict with normalised labels.
        """

        for key in ["pre_l", "post_l", "post_n1"]:
            tempattr: Optional[str] = getattr(self, key, None)
            if tempattr is None:
                continue
            if key == "pre_l":
                if tempattr in ["a", "alpha"]:
                    setattr(self, key, "a")
                elif tempattr in ["b", "beta"]:
                    setattr(self, key, "b")
                elif tempattr in ["c", "rc", "pre", "preview"]:
                    setattr(self, key, "rc")
            elif key == "post_l":
                setattr(self, key, "post")
            elif key == "post_n1":
                setattr(self, key, None)
                setattr(self, "post_l", "post")
                setattr(self, "post_n2", tempattr)
        return self

    def add_implicit_zeros(self) -> VersionDict:
        """
        Adds the implicit zeros to version.

        Returns:
            VersionDict: VersionDict with the implicit zeros added.
        """

        for key_l, key_n in VERSION_IMPLICIT_KEYS:
            if (
                getattr(self, key_l)  # Checks if key exists.
                and getattr(self, key_n) is None  # Number is None
            ):
                setattr(self, key_n, "0")
        return self

    def __str__(self) -> str:
        """
        Constructs a valid version string from a dictionary of keys
        from version
        regex.

        Returns:
            str: A valid version string.

        Raises:
            VersionKeyError: Unexpected key in VERSION_KEYS.
        """
        ret_version = ""
        for key in VERSION_KEYS:
            tempattr = getattr(self, key, None)
            if tempattr is None:
                continue
            if key == "v":
                ret_version += "v"
            elif key == "epoch":
                ret_version += tempattr + "!"
                continue
            elif key == "local_l":
                ret_version += "+" + tempattr
                continue
            elif key in VERSION_DOTTED_SEGMENT:
                ret_version += "." + tempattr
            elif key == "post_l":
                ret_version += ".post"
            elif key in VERSION_KEYS:
                ret_version += tempattr
            else:
                raise VersionKeyError(f"Unexpected key: {key}")
        return ret_version

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{str(self)}')"
