"""
main.py



Author: Zack Hankin

Started: 4/03/2023
"""
from __future__ import annotations

from .version_api import fetch_version


def main() -> int:
    """
    Main function for api.

    Returns:
        int: Exit code
    """
    print(fetch_version())
    return 0
