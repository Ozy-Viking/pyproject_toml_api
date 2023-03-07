"""
Version Util

Author: Zack Hankin

Started: 6/03/2023
"""
from __future__ import annotations

import re

VERSION_PATTERN: str = r"""
    (?P<v>v)?
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
VERSION_INT_KEYS: set[str] = {
    "epoch",
    "major",
    "minor",
    "patch",
    "pre_n",
    "post_n1",
    "post_n2",
    "dev_n",
}
VERSION_IMPLICIT_KEYS: set[tuple[str, str]] = {
    ("pre_l", "pre_n"),
    ("post_l", "post_n2"),
    ("dev_l", "dev_n"),
}
VERSION_KEYS: list[str] = [
    "v",
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
VERSION_LABELS: list[str] = [
    "pre_l",
    "post_l",
    "dev_l",
    "local_l",
]
VERSION_DOTTED_SEGMENT: set[str] = {
    "minor",
    "patch",
    "post_n1",
    "dev_l",
    "local_n",
}


class VersionError(Exception):
    pass


class VersionTypeError(VersionError, TypeError):
    pass


class VersionSyntaxError(VersionError, SyntaxError):
    pass


class VersionKeyError(VersionError, KeyError):
    pass
